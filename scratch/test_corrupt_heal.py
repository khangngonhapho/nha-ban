import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

# Corrupt credentials.json in workspace
print("Corrupting credentials.json in workspace...")
with open("credentials.json", "w", encoding="utf-8") as f:
    f.write('{"type": "service_account", "project_id": "corrupted"}')

# Import curator_server and trigger credentials load
import curator_server

print("Calling get_google_credentials()...")
creds = curator_server.get_google_credentials()
print("Creds returned:", creds)

# Read credentials.json to verify it got healed
with open("credentials.json", "r", encoding="utf-8") as f:
    content = f.read()
    
print("New credentials.json contents preview:", content[:50])
print("Is it valid JSON now?", content.startswith("{") and "khangngo-admin" in content)
