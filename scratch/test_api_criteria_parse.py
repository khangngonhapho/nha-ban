# -*- coding: utf-8 -*-
import sys
import json
import os

sys.path.insert(0, os.getcwd())
import fetcher

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    json_file = "scratch/detail_TKQLMB8Q.json"
    if not os.path.exists(json_file):
        print(f"File {json_file} not found!")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    detail_data = data.get("data") or {}
    criteria_list = detail_data.get("criteria") or []
    
    print(f"Total criteria items in JSON: {len(criteria_list)}")
    
    res = fetcher.parse_criteria_groups(criteria_list)
    print("\nParsed criteria columns:")
    for k, v in res.items():
        print(f"  {k}: {repr(v)}")

if __name__ == "__main__":
    main()
