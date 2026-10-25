import os
import sys
import json
import requests

print("==================================================================")
print("🛡️ Starting Terraform State Security Analyzer...")
print("==================================================================\n")

GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_KEY:
    print("❌ Error: Missing GEMINI_API_KEY. Run: export GEMINI_API_KEY='your_key'")
    sys.exit(1)

gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_KEY}"
headers = {"Content-Type": "application/json"}

def load_tf_plan(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Failed to read Terraform plan: {e}")
        sys.exit(1)

def analyze_infrastructure_risk(plan_data):
    print("🔍 Scanning Terraform plan for hardcoded secrets, destructive actions, and drift...")
    
    prompt = f"""
    You are a Principal Cloud Security Architect. 
    Review the following Terraform plan JSON output. 
    
    Your objective is to identify:
    1. Destructive actions (e.g., deleting production databases).
    2. Hardcoded secrets (passwords, tokens) that should be migrated to HashiCorp Vault. Provide the exact Vault integration syntax.
    3. Network security risks (e.g., SSH open to the world).
    
    Output a formal DevSecOps Risk Assessment that would be posted automatically as a GitHub PR comment.
    
    Terraform Plan JSON:
    {json.dumps(plan_data, indent=2)}
    """
    
    try:
        print("🧠 Querying AI Security Architect...\n")
        response = requests.post(gemini_url, headers=headers, json={"contents": [{"parts": [{"text": prompt}]}]})
        response.raise_for_status()
        print("="*70)
        print("🛑 AUTOMATED DEVSECOPS PR REVIEW 🛑")
        print("="*70)
        print(response.json()['candidates'][0]['content']['parts'][0]['text'])
        print("="*70 + "\n")
    except Exception as e:
        print(f"❌ AI Analysis Failed: {e}")

if __name__ == '__main__':
    plan_path = "ai-observability/terraform-data/tf_plan.json"
    plan_json = load_tf_plan(plan_path)
    analyze_infrastructure_risk(plan_json)
