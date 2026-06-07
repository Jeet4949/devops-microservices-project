import os
import requests
import json
import sys

print("==================================================================")
print("🏗️  Welcome to the AI Internal Developer Platform (IDP) Console")
print("==================================================================")
print("Type 'exit' to gracefully terminate the session.\n")

# 1. Verify access to Google AI Credentials
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

if not GEMINI_KEY:
    print("❌ Error: Missing GEMINI_API_KEY environment variable.")
    print("Please run: export GEMINI_API_KEY='your_key_here'")
    sys.exit(1)

# Utilizing the high-velocity, code-optimized Gemini 3.5 Flash model
gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_KEY}"
headers = {"Content-Type": "application/json"}

while True:
    developer_intent = input("👨‍💻 Describe the AWS infrastructure requirements: \n> ")
    
    if developer_intent.strip().lower() == 'exit':
        print("\n👋 Closing cloud architect session. Secure deployments!")
        break

    if not developer_intent.strip():
        continue

    print("\n🤖 AI Architect is parsing intent and compiling HCL infrastructure...")

    # Strict system instruction boundary to guarantee structural output format
    prompt = f"""
    You are a Principal Cloud Infrastructure Architect. Translate the following natural language request into high-availability, secure AWS Terraform code (HCL).
    
    USER REQUEST: {developer_intent}
    
    STRICT COMPILATION RULES:
    1. Output ONLY valid, parseable Terraform HCL code.
    2. Do NOT wrap the output in markdown text wrappers (such as ```terraform or ```hcl).
    3. Do NOT include introductory greetings, explanatory paragraphs, or concluding annotations.
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(gemini_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse output payload safely
        result_json = response.json()
        tf_code = result_json['candidates'][0]['content']['parts'][0]['text']
        
        # Defensive regex-like cleaning to ensure absolute clean code compilation
        tf_code = tf_code.replace('```terraform\n', '').replace('```hcl\n', '').replace('```', '').strip()

        # Write output code to the designated environment location
        file_path = "idp-chat-agent/generated_infra/main.tf"
        with open(file_path, "w") as tf_file:
            tf_file.write(tf_code)

        print("------------------------------------------------------------------")
        print(f"✅ Success! Compiled configuration written to: {file_path}")
        print("------------------------------------------------------------------\n")

    except Exception as e:
        print(f"❌ Execution Failure: Unable to synthesize code. Details: {e}\n")
