import os
import sys
import requests
from fastapi import FastAPI, Request
import uvicorn
from kubernetes import client, config

app = FastAPI()

# Setup Gemini API (Using our locked-in 3.5 model)
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_KEY:
    print("❌ Error: Missing GEMINI_API_KEY. Run: export GEMINI_API_KEY='your_key'")
    sys.exit(1)
    
gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_KEY}"
headers = {"Content-Type": "application/json"}

# Connect to local K8s
try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
    print("✅ Connected to Kubernetes Cluster.")
except Exception as e:
    print(f"❌ Failed to connect to Kubernetes: {e}")
    sys.exit(1)

def generate_rca(pod_name, namespace, alert_name, logs, events):
    prompt = f"""
    You are a Principal AI Incident Commander responding to a PagerDuty alert.
    
    Alert Name: {alert_name}
    Failing Pod: {pod_name} (Namespace: {namespace})
    
    Recent Cluster Events:
    {events}
    
    Recent Container Logs:
    {logs}
    
    Draft a formal Incident Report for the SRE team. Include:
    1. Incident Summary
    2. Root Cause Analysis (based on the logs/events provided)
    3. Immediate Remediation Steps (provide exact kubectl commands)
    """
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(gemini_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ AI Analysis Failed: {str(e)}"

@app.post("/webhook")
async def alertmanager_webhook(request: Request):
    payload = await request.json()
    print("\n🚨 [ALERT RECEIVED] Intercepted webhook from Prometheus/Alertmanager!")
    
    # Parse the incoming Prometheus alert payload
    alerts = payload.get("alerts", [])
    for alert in alerts:
        labels = alert.get("labels", {})
        alert_name = labels.get("alertname", "Unknown Alert")
        pod_name = labels.get("pod", "unknown-pod")
        namespace = labels.get("namespace", "default")
        
        print(f"🔍 Investigating: '{alert_name}' on pod '{pod_name}'...")
        
        # 1. Fetch Events
        events_str = "No recent events."
        try:
            events = v1.list_namespaced_event(namespace, field_selector=f"involvedObject.name={pod_name}")
            if events.items:
                events_str = "\n".join([f"- {e.message}" for e in events.items[-5:]])
        except Exception as e:
            events_str = f"Could not fetch events: {e}"
            
        # 2. Fetch Logs
        logs_str = "No logs available (pod might be stuck in ImagePullBackOff or Pending state)."
        try:
            logs_str = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=20)
        except Exception:
            pass 

        # 3. Generate RCA
        print("🧠 Compiling context and querying AI Incident Commander...\n")
        rca_report = generate_rca(pod_name, namespace, alert_name, logs_str, events_str)
        
        print("="*70)
        print(f"📑 AUTOMATED INCIDENT TICKET: {alert_name}")
        print("="*70)
        print(rca_report)
        print("="*70 + "\n")

    return {"status": "Incident Report Generated successfully"}

if __name__ == "__main__":
    print("==================================================================")
    print("🤖 Starting AI Incident Commander Webhook Server on port 8080...")
    print("==================================================================")
    uvicorn.run(app, host="0.0.0.0", port=8080)
