import os
import sys
import json
import subprocess
import requests

# Fail-safe absolute path injection to resolve local scripts
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from context_harvester import find_relevant_callers
except ImportError:
    print("❌ Failed to import context_harvester.py. Please ensure it is in the same directory.")
    sys.exit(1)

def get_modified_files():
    try:
        files = subprocess.check_output(["git", "diff", "--name-only", "origin/main...HEAD", "--", ".", ":!.github/"], text=True)
        if not files.strip():
            files = subprocess.check_output(["git", "status", "--porcelain", "--", ".", ":!.github/"], text=True)
            files = [line.strip().split()[-1] for line in files.splitlines() if line.strip()]
        else:
            files = files.splitlines()
        return [f.strip() for f in files if f.strip()]
    except Exception as e:
        print(f"Error getting modified files list: {e}")
        return []

def get_local_git_diff():
    try:
        diff = subprocess.check_output(["git", "diff", "origin/main...HEAD", "--", ".", ":!.github/"], text=True)
        if not diff.strip():
            diff = subprocess.check_output(["git", "diff", "HEAD", "--", ".", ":!.github/"], text=True)
        return diff
    except Exception as e:
        print(f"Error getting git diff: {e}")
        sys.exit(1)

def get_surrounding_tests(modified_files):
    surrounding_content = ""
    for file in modified_files:
        if file.endswith(".py") and not file.startswith("tests/"):
            filename = os.path.basename(file)
            test_filename = f"test_{filename}"
            possible_test_paths = [
                os.path.join("tests", test_filename),
                os.path.join("test", test_filename),
                file.replace("src/", "tests/test_"),
            ]
            for test_path in possible_test_paths:
                if os.path.exists(test_path):
                    try:
                        with open(test_path, 'r') as f:
                            surrounding_content += f"\n\n=== Surrounding Context: Test Suite File: {test_path} ===\n"
                            surrounding_content += f.read()
                        print(f"📌 Attached surrounding test file: {test_path}")
                        break
                    except Exception as e:
                        print(f"Error reading test file {test_path}: {e}")
    return surrounding_content

def run_local_tests():
    print("🧪 Running local test suite to capture runtime feedback...")
    try:
        result = subprocess.run(["pytest"], capture_output=True, text=True, timeout=30)
        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            print("✅ All local tests passed!")
            return "\n=== Runtime Context: Test Suite Results ===\nAll tests passed successfully.\n"
        else:
            print("⚠️ Some local tests failed! Capturing tracebacks for the AI...")
            return f"\n=== Runtime Context: Test Suite Failures ===\n{output}\n"
    except FileNotFoundError:
        print("ℹ️ Pytest not found, skipping test run.")
        return ""
    except Exception as e:
        return f"\n=== Runtime Context: Test Suite Status ===\nError running tests: {e}\n"

def get_gh_token():
    try:
        token = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
        return token
    except Exception as e:
        print("Error: Could not retrieve GitHub token. Ensure you are logged in via 'gh auth login'.")
        sys.exit(1)

def post_to_github_pr():
    print("💬 Checking for an active Pull Request on GitHub...")
    try:
        subprocess.check_output(["gh", "pr", "view", "--json", "number"], text=True)
        print("📤 Posting the review report as a comment on your PR...")
        subprocess.run(["gh", "pr", "comment", "-F", "review_report.md"], check=True)
        print("🎉 Success! Review comment posted directly to your Pull Request on GitHub.")
    except subprocess.CalledProcessError:
        print("ℹ️ Note: No open Pull Request found for this branch on GitHub yet.")

def main():
    print("🔄 Local Review Agent (V2-AST): Fetching local session...")
    token = get_gh_token()
    pr_diff = get_local_git_diff()
    modified_files = get_modified_files()

    if not pr_diff.strip():
        print("⚠️ No functional application changes found to review.")
        sys.exit(0)

    test_context = get_surrounding_tests(modified_files)
    print("📂 Analyzing repository dependencies using AST parsing...")
    caller_context = find_relevant_callers(modified_files)
    test_results = run_local_tests()

    with open(".github/copilot-instructions.md", 'r') as f: instructions = f.read()
    with open(".github/prompts/code-review.prompt.md", 'r') as f: prompt_template = f.read()

    ide_headers = {"User-Agent": "GitHubCopilotChat/0.39.0","Editor-Version": "vscode/1.99.0"}
    copilot_auth_headers = {"Authorization": f"token {token}", **ide_headers}
    copilot_auth_res = requests.get("https://api.github.com/copilot_internal/v2/token", headers=copilot_auth_headers)
    if copilot_auth_res.status_code != 200:
        print(f"❌ Failed to authorize with Copilot token exchange: {copilot_auth_res.text}")
        sys.exit(1)
        
    copilot_token = copilot_auth_res.json().get("token")
    base_api_url = copilot_auth_res.json().get("endpoints", {}).get("api", "https://api.githubcopilot.com")
    completions_url = f"{base_api_url}/chat/completions"

    print("🧠 Sending diff, static context, dependency graph, and runtime logs to Copilot...")
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": f"System instructions:\n{instructions}"},
            {"role": "user", "content": f"Perform a code review based on the template guidelines.\n\nTemplate:\n{prompt_template}\n\nGit Diff:\n{pr_diff}\n\n{test_context}\n\n{caller_context}\n\n{test_results}"}
        ],
        "temperature": 0.1
    }
    
    llm_headers = {"Authorization": f"Bearer {copilot_token}", "Content-Type": "application/json", **ide_headers}
    llm_res = requests.post(completions_url, headers=llm_headers, json=payload)
    if llm_res.status_code != 200:
        print(f"❌ Error calling Copilot LLM: {llm_res.text}")
        sys.exit(1)

    review_content = llm_res.json()["choices"][0]["message"]["content"]
    
    with open("review_report.md", "w") as f: f.write(review_content)
    print(f"\n🎉 Success! Standardized review output saved to 'review_report.md'\n")

    post_to_github_pr()

if __name__ == "__main__":
    main()
