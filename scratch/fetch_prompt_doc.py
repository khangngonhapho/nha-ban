import os
import sys
import json
import re

# Add project root to path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials, get_google_access_token

import requests

def main():
    doc_id = "1-VlvYmwY9_22dULAF4Xtlooa8A8VUfiV3OVU01OaoGE"
    creds = get_google_credentials()
    if not creds:
        print("Error: credentials.json not found or invalid.")
        return
        
    token = get_google_access_token(creds)
    if not token:
        print("Error: Could not generate access token.")
        return
        
    url = f"https://www.googleapis.com/drive/v3/files/{doc_id}/export?mimeType=text/plain"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Fetching Google Doc: {doc_id}...")
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        content = res.text
        if content.startswith('\ufeff'):
            content = content[1:]
        print("\n=== GOOGLE DOC CONTENT ===\n")
        print(content)
        print("\n==========================\n")
        
        # Save to scratch folder for reference
        with open("scratch/google_doc_prompt.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved to scratch/google_doc_prompt.txt")
    else:
        print(f"Failed to fetch Google Doc, status {res.status_code}: {res.text}")

if __name__ == "__main__":
    main()
