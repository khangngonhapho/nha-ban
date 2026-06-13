import os
import json

files = [
    "credentials.json.bak",
    "khangngo-admin-a96043c2f638.json"
]

for f in files:
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
            print(f"File: {f}")
            print(f"  Keys: {list(data.keys())}")
            print(f"  Type: {data.get('type')}")
            print(f"  Client Email: {data.get('client_email')}")
            print(f"  Project ID: {data.get('project_id')}")
        except Exception as e:
            print(f"Error loading {f}: {e}")
    else:
        print(f"File {f} does not exist!")
