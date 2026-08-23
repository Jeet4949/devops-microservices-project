import os
import sys
import requests
from kubernetes import client, config

print("==================================================================")
print("🥷 Starting FinOps Cost Assassin Agent...")
print("==================================================================\n")

GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_KEY:
    print("❌ Error: Missing GEMINI_API_KEY. Run: export GEMINI_API_KEY='your_key'")
    sys.exit(1)

# Using the stable 3.5 model we locked in earlier
gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_KEY}"
headers = {"Content-Type": "application/json"}

try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
    print("✅ Connected to Kubernetes Cluster.")
except Exception as e:
    print(f"❌ Failed to connect to Kubernetes: {e}")
    sys.exit(1)

def generate_finops_report(waste_data):
    print("\n🧠 Sending cluster telemetry to AI FinOps Architect...")
    prompt = f"""
    You are a Principal FinOps Architect and Kubernetes Expert. 
    Analyze the following Kubernetes cluster waste data and provide a concise, aggressive cost-optimization plan.
    Include exact kubectl commands to clean up orphaned resources and YAML snippets to set baseline resource limits.
    
    Cluster Waste Data:
    {waste_data}
    """
    try:
        response = requests.post(gemini_url, headers=headers, json={"contents": [{"parts": [{"text": prompt}]}]})
        response.raise_for_status()
        print("\n" + "="*60)
        print("💰 AI FINOPS OPTIMIZATION PLAN 💰")
        print("="*60)
        print(response.json()['candidates'][0]['content']['parts'][0]['text'])
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ AI Analysis Failed: {e}")

def hunt_for_waste():
    print("🔍 Scanning cluster for orphaned volumes and oversized pods...\n")
    waste_report = []
    
    # 1. Check for Unbound PVCs (Paying for AWS/GCP storage you aren't using)
    pvcs = v1.list_persistent_volume_claim_for_all_namespaces().items
    unbound_pvcs = [p.metadata.name for p in pvcs if p.status.phase != "Bound"]
    if unbound_pvcs:
        waste_report.append(f"Unbound/Orphaned PVCs (Wasted Disk Space): {', '.join(unbound_pvcs)}")
        
    # 2. Check for Pods without Resource Limits (Risk of Node Bloat & Cloud Autoscaler Spikes)
    pods = v1.list_pod_for_all_namespaces().items
    greedy_pods = []
    for pod in pods:
        for container in pod.spec.containers:
            if not container.resources or (not container.resources.limits and not container.resources.requests):
                greedy_pods.append(pod.metadata.name)
                break
                
    if greedy_pods:
        waste_report.append(f"Pods with NO Resource Limits (Autoscaler Risk): {', '.join(greedy_pods[:10])}")
        
    if not waste_report:
        print("🟢 Cluster is lean and optimized! No obvious waste detected.")
    else:
        for alert in waste_report:
            print(f"⚠️  DETECTED WASTE: {alert}")
        generate_finops_report("\n".join(waste_report))

if __name__ == '__main__':
    hunt_for_waste()
