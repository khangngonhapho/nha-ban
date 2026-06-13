import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

folder_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"

if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    print("=== Scanning JS Bundles for API Paths ===")
    
    # We want to find strings that look like API endpoints, e.g. /api/... or /warehouse/... or /sources/...
    # Let's search inside the .js files
    js_files = [f for f in files if f.endswith((".js", "tải xuống")) and not any(term in f for term in ["map.js", "util.js", "common.js", "places.js", "main.js"])]
    
    for f in js_files:
        fpath = os.path.join(folder_path, f)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_in:
                content = file_in.read()
            
            # Find occurrences of '/api/'
            api_calls = re.findall(r'"/[a-zA-Z0-9_\-\/]+/api/[a-zA-Z0-9_\-\/]+"|\'/api/[a-zA-Z0-9_\-\/]+\'|"/api/[a-zA-Z0-9_\-\/]+"', content)
            # Find any references to 'warehouse' or 'sources'
            warehouse_refs = re.findall(r'"/[a-zA-Z0-9_\-\/]*warehouse[a-zA-Z0-9_\-\/]*"|\'/a-zA-Z0-9_\-\/]*warehouse[a-zA-Z0-9_\-\/]*\'|/warehouse/[a-zA-Z0-9_\-\/]+', content)
            
            if api_calls or warehouse_refs:
                print(f"\nIn file: {f}")
                if api_calls:
                    print(f"  Sample API calls: {list(set(api_calls))[:10]}")
                if warehouse_refs:
                    print(f"  Sample Warehouse refs: {list(set(warehouse_refs))[:10]}")
                    
                # Let's search for "sources" references
                sources_refs = re.findall(r'"/api/[a-zA-Z0-9_\-\/]*sources[a-zA-Z0-9_\-\/]*"|/sources/[a-zA-Z0-9_\-\/]+', content)
                if sources_refs:
                    print(f"  Sample Sources refs: {list(set(sources_refs))[:10]}")
                    
                # Let's search for things containing "detail" or "legal" or "owner" or "homeowner"
                for term in ["detail", "legal", "owner", "homeowner", "phone", "sodo", "sổ đỏ"]:
                    matches = re.findall(rf'"/[a-zA-Z0-9_\-\/]*{term}[a-zA-Z0-9_\-\/]*"', content, re.I)
                    if matches:
                        print(f"  Matches for '{term}': {list(set(matches))[:5]}")
        except Exception as e:
            print(f"Error reading {f}: {e}")
else:
    print("Folder does not exist")
