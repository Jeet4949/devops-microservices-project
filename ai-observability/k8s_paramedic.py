import os
import sys
import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException

print("==================================================================")
print("🚑 Starting Autonomous K8s Paramedic Agent...")
print("==================================================================\n")

GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_KEY:
    print("❌ Error: Missing GEMINI_API_KEY. Run: export GEMINI_API_KEY='your_key'")
    sys.exit(1)

gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_KEY}"
headers = {"Content-Type": "application/json"}

try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
    print("✅ Connected to Kubernetes Cluster.")
except Exception as e:
    print(f"❌ Failed to connect to Kubernetes: {e}")
    sys.exit(1)

def analyze_failure_with_ai(pod_name, namespace, error_reason, events):
    print(f"\n🧠 Sending telemetry for {pod_name} to AI SRE for root cause analysis...")
    
    prompt = f"""
    You are a Principal Kubernetes Site Reliability Engineer (SRE). 
    A pod in my cluster is failing. 
    
    Pod Name: {pod_name}
    Namespace: {namespace}
    Failure Reason: {error_reason}
    Recent Cluster Events for this Pod: 
    {events}
    
    Provide a concise Root Cause Analysis (RCA) and the exact kubectl commands or YAML changes needed to fix this issue.
    Keep the response highly technical and actionable.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(gemini_url, headers=headers, json=payload)
        response.raise_for_status()
        ai_diagnosis = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        print("\n" + "="*60)
        print("🚨 AI ROOT CAUSE ANALYSIS & REMEDIATION 🚨")
        print("="*60)
        print(ai_diagnosis)
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ AI Analysis Failed: {e}")

def scan_cluster():
    print("🔍 Scanning all namespaces for failing pods...\n")
    try:
        pods = v1.list_pod_for_all_namespaces(watch=False)
        sick_pods_found = False

        for pod in pods.items:
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    state = container.state
                    
                    if (state.waiting and state.waiting.reason != "ContainerCreating") or \
                       (state.terminated and state.terminated.exit_code != 0):
                        
                        sick_pods_found = True
                        reason = state.waiting.reason if state.waiting else state.terminated.reason
                        print(f"⚠️  DETECTED FAILING POD: {pod.metadata.name} (Namespace: {pod.metadata.namespace}) - Reason: {reason}")
                        
                        events = v1.list_namespaced_event(pod.metadata.namespace, field_selector=f"involvedObject.name={pod.metadata.name}")
                        event_logs = "\n".join([f"- {e.message}" for e in events.items[-5:]])
                        
                        if not event_logs:
                            event_logs = "No recent events found. Container might be crash-looping silently."

                        analyze_failure_with_ai(pod.metadata.name, pod.metadata.namespace, reason, event_logs)

        if not sick_pods_found:
            print("🟢 Cluster is perfectly healthy! No failing pods detected.")

    except ApiException as e:
        print(f"❌ Kubernetes API Error: {e}")

if __name__ == '__main__':
    scan_cluster()
