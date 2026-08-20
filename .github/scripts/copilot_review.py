import os
import sys
import json
import requests

def main():
    token = os.getenv("GITHUB_TOKEN")
    event_path = os.getenv("GITHUB_EVENT_PATH")
    
    if not token or not event_path:
        print("Missing GITHUB_TOKEN or GITHUB_EVENT_PATH")
        sys.exit(1)

    # 1. Load PR metadata
    with open(event_path, 'r') as f:
        event_data = json.load(f)
        
    pr_number = event_data["pull_request"]["number"]
    repo_name = event_data["repository"]["full_name"]
    api_url = event_data["repository"]["url"]

    print(f"Analyzing PR #{pr_number} for {repo_name}...")

    # 2. Get PR Diff
    diff_headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    diff_res = requests.get(f"{api_url}/pulls/{pr_number}", headers=diff_headers)
    if diff_res.status_code != 200:
        print("Failed to fetch PR diff")
        sys.exit(1)
    pr_diff = diff_res.text

    # 3. Read prompt files
    instructions_path = ".github/copilot-instructions.md"
    prompt_path = ".github/prompts/code-review.prompt.md"
    
    instructions = ""
    prompt_template = ""
    
    if os.path.exists(instructions_path):
        with open(instructions_path, 'r') as f:
            instructions = f.read()
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()

    # 4. Request Copilot Auth Token using GitHub Token
    # This leverages the Action runner's access to Copilot
    copilot_auth_headers = {
        "Authorization": f"token {token}",
        "User-Agent": "Copilot-PR-Reviewer"
    }
    copilot_auth_res = requests.get("https://api.github.com/copilot_internal/v2/token", headers=copilot_auth_headers)
    if copilot_auth_res.status_code != 200:
        print("This repository/organization does not have Copilot enabled for Actions, or the token is unauthorized.")
        sys.exit(1)
        
    copilot_token_data = copilot_auth_res.json()
    copilot_token = copilot_token_data.get("token")

    # 5. Call Copilot LLM Engine (GPT-4o API endpoint)
    payload = {
        "model": "gpt-4o", # Target Copilot's default review engine
        "messages": [
            {"role": "system", "content": f"You are a Senior Staff Engineer. Follow these system instructions for code reviews:\n{instructions}"},
            {"role": "user", "content": f"Perform a code review on the following git diff based on the requested template guidelines:\n\nTemplate Guidelines:\n{prompt_template}\n\nGit Diff:\n{pr_diff}"}
        ],
        "temperature": 0.1
    }
    
    llm_headers = {
        "Authorization": f"Bearer {copilot_token}",
        "Content-Type": "application/json",
        "User-Agent": "Copilot-PR-Reviewer"
    }
    
    # We query the official underlying endpoint of the GitHub Copilot API
    llm_res = requests.post("https://api.githubapi.com/copilot/chat/completions", headers=llm_headers, json=payload)
    if llm_res.status_code != 200:
        # Fallback endpoint if API URL routes differently
        llm_res = requests.post("https://api.github.com/copilot/chat/completions", headers=llm_headers, json=payload)
        
    if llm_res.status_code != 200:
        print(f"Error calling Copilot LLM: {llm_res.status_code} {llm_res.text}")
        sys.exit(1)

    review_content = llm_res.json()["choices"][0]["message"]["content"]

    # 6. Post the review as a PR comment
    comment_headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    comment_payload = {"body": review_content}
    comment_res = requests.post(f"{api_url}/issues/{pr_number}/comments", headers=comment_headers, json=comment_payload)
    
    if comment_res.status_code == 201:
        print("Success! Posted the standardized review comment on the PR.")
    else:
        print(f"Failed to post comment: {comment_res.status_code} {comment_res.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
