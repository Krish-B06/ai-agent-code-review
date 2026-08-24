import os
import sys
import json
import subprocess
import requests

# Fail-safe import of our context harvester
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)
from context_harvester import find_relevant_callers

# --- Environment Detection ---
IS_CI = os.getenv("CI") == "true"

def get_diff():
    """Gets the git diff based on the environment (local vs. CI)."""
    try:
        if IS_CI:
            base_ref = os.getenv("GITHUB_BASE_REF", "main")
            print(f"CI environment detected. Diffing against base branch: origin/{base_ref}")
            subprocess.run(["git", "fetch", "origin", base_ref], check=True) # Ensure base branch is available
            return subprocess.check_output(["git", "diff", f"origin/{base_ref}...", "HEAD", "--", ".", ":!.github/"]).decode()
        else:
            print("Local environment detected. Diffing against main branch.")
            return subprocess.check_output(["git", "diff", "origin/main...", "HEAD", "--", ".", ":!.github/"]).decode()
    except subprocess.CalledProcessError:
        return ""

def get_modified_files():
    """Gets a list of modified files based on the environment."""
    try:
        if IS_CI:
            base_ref = os.getenv("GITHUB_BASE_REF", "main")
            files_str = subprocess.check_output(["git", "diff", "--name-only", f"origin/{base_ref}...", "HEAD", "--", ".", ":!.github/"]).decode()
        else:
            files_str = subprocess.check_output(["git", "diff", "--name-only", "origin/main...", "HEAD", "--", ".", ":!.github/"]).decode()
        return [f.strip() for f in files_str.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        return []

def post_review_comment(report_content):
    """Posts the review comment using the appropriate tool for the environment."""
    if IS_CI:
        pr_number = os.getenv("PR_NUMBER")
        repo = os.getenv("GITHUB_REPOSITORY")
        token = os.getenv("GITHUB_TOKEN")
        if not all([pr_number, repo, token]):
            print("Error: Missing CI environment variables for posting comment.")
            return
        
        print(f"Posting comment to PR #{pr_number} via GitHub API...")
        url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        body = {"body": report_content}
        res = requests.post(url, headers=headers, json=body)
        if res.status_code == 201:
            print("🎉 Success! Review posted to PR.")
        else:
            print(f"❌ Failed to post comment: {res.status_code} {res.text}")
    else:
        # On a local machine, use the gh CLI
        print("Posting comment via local gh CLI...")
        try:
            with open("review_report.md", "w") as f: f.write(report_content)
            subprocess.run(["gh", "pr", "comment", "-F", "review_report.md"], check=True, capture_output=True, text=True)
            print("🎉 Success! Review posted to PR.")
        except subprocess.CalledProcessError as e:
            print(f"ℹ️ No active PR found, or gh CLI failed: {e.stderr}")


def run_tests():
    """Runs the pytest suite and captures the output."""
    print("🧪 Running test suite...")
    try:
        result = subprocess.run(["pytest"], capture_output=True, text=True, check=False)
        return f"--- Test Suite Results ---\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"--- Test Suite Error ---\nCould not run tests: {e}"

def main():
    print("🔄 AI Code Review Agent Initializing...")
    
    diff = get_diff()
    modified_files = get_modified_files()

    if not diff.strip():
        print("✅ No changes detected to review. Exiting.")
        return

    caller_context = find_relevant_callers(modified_files)
    test_results = run_tests()
    
    # This is the corrected f-string that will properly inject the variables.
    report = f"""
# 🤖 AI Code Review Report (Generated in {'CI' if IS_CI else 'Local'} Mode)

This review was generated automatically by the V2 agent.

## Analysis Summary

- **Test Suite:** The complete test suite was executed.
- **Dependency Analysis:** The codebase was scanned for any files that depend on your changes.

---

### Test Suite Output
{test_results}

---

### Cross-File Dependency Context
The following files depend on the code you changed and were included in the analysis:

{caller_context if caller_context else "No external callers were found."}

---

### Git Diff Analyzed
The following changes triggered this review:
```diff
{diff[:3000]}...
(Diff truncated for brevity)

"""

print("\n--- Generated Review Report ---") print(report) print("-----------------------------\n") post_review_comment(report)
if name == "main":
main()
