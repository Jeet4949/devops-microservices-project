import os
import requests
import json

print("🤖 Starting Gemini AI Code Reviewer...")

# 1. Fetch environment variables from GitHub Actions
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO = os.environ.get('GITHUB_REPOSITORY')
PR_NUMBER = os.environ.get('PR_NUMBER')

if not GEMINI_KEY or not GITHUB_TOKEN or not PR_NUMBER:
    print("❌ Error: Missing required environment variables.")
    exit(1)

# 2. Setup GitHub API client headers
github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff"  # Request raw code differences
}

# --- PHASE 1: Fetch the Code Changes (The Diff) ---
diff_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
print(f"Fetching diff from: {diff_url}")

try:
    response = requests.get(diff_url, headers=github_headers)
    response.raise_for_status()
    pr_diff_content = response.text
except Exception as e:
    print(f"❌ Error fetching PR diff: {e}")
    exit(1)

if not pr_diff_content:
    print("⚠️ No code changes found in this PR.")
    exit(0)

# --- PHASE 2: Send the Diff to Gemini ---
print("Sending diff to Gemini Pro for analysis...")

# Prompt design for structural code reviews
prompt = f"""
You are a Senior DevOps and Platform Engineer performing a rigorous code review.
Analyze the provided code changes (diff format). These changes may contain Python microservices code or Terraform code.

Focus your review on these areas:
1. SECURITY VULNERABILITIES: Check for hardcoded secrets, database passwords, or API keys. Verify that secrets are managed via dynamic injection (e.g. HashiCorp Vault).
2. BUGS & LOGIC ERRORS: Identify logical flaws or potential runtime exceptions in the Python code.
3. KUBERNETES/TERRAFORM PRACTICES: Ensure infrastructure changes adhere to production standards.

Format your response in clear Markdown. Be constructive. Start with a brief summary, then use structured headers (## Security, ## Bugs, etc.) and use code blocks for suggestions.

THE CODE DIFF TO REVIEW:
{pr_diff_content}
"""

# Call Gemini API directly via HTTP POST using the standard developer endpoint
gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_KEY}"
gemini_payload = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}
gemini_headers = {"Content-Type": "application/json"}

try:
    gemini_response = requests.post(gemini_url, headers=gemini_headers, json=gemini_payload)
    gemini_response.raise_for_status()
    result_json = gemini_response.json()
    # Extract text from the Gemini response structure
    ai_review_feedback = result_json['candidates'][0]['content']['parts'][0]['text']
except Exception as e:
    print(f"❌ Error during Gemini API generation: {e}")
    if 'gemini_response' in locals():
        print(f"Response details: {gemini_response.text}")
    exit(1)

# --- PHASE 3: Post the Gemini Feedback Back to the PR ---
print("Gemini review complete. Posting feedback back to GitHub...")
comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"

github_headers["Accept"] = "application/vnd.github.v3+json"
payload = {"body": f"### 🤖 Gemini Automated Code Review\n\n{ai_review_feedback}"}

try:
    response = requests.post(comment_url, headers=github_headers, json=payload)
    response.raise_for_status()
    print("✅ Success! Gemini code review posted successfully.")
except Exception as e:
    print(f"❌ Error posting comment to GitHub: {e}")
    exit(1)
