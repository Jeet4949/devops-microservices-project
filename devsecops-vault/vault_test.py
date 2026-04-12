import hvac
import os

print("🤖 Starting Microservice...")

# 1. Connect to the local Vault server
client = hvac.Client(
    url=os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200'),
    token=os.environ.get('VAULT_TOKEN')
)

# 2. Verify the connection
if client.is_authenticated():
    print("✅ Successfully authenticated with HashiCorp Vault!")
else:
    print("❌ Vault connection failed. Check your token.")
    exit()

# 3. Request the secret from the Vault
print("Fetching database credentials securely...\n")
try:
    response = client.secrets.kv.v2.read_secret_version(path='my-database')
    
    credentials = response['data']['data']
    username = credentials['username']
    password = credentials['password']
    
    print("--- SECURE DATA INJECTED ---")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("----------------------------")
    print("\n🔐 Success! Application connected to DB without hardcoded secrets.")
    
except Exception as e:
    print(f"Error reading secret: {e}")
