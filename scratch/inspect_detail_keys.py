import json
import os
import sys

json_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/detail_TKQLMB8Q.json"
output_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/inspect_detail_keys_output.txt"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

prop_data = data.get("data", {})

lines = []
lines.append("--- Root Level Keys and Sample Values ---")
for k, v in prop_data.items():
    if k == "criteria":
        lines.append(f"- criteria: list of {len(v)} items")
    elif k == "media":
        lines.append(f"- media: list of {len(v)} items")
    elif k == "ownerSideUser":
        lines.append(f"- ownerSideUser: dict with keys {list(v.keys())}")
    elif k == "homeOwner":
        lines.append(f"- homeOwner: list of {len(v)} items")
    elif isinstance(v, (dict, list)):
        lines.append(f"- {k}: {type(v).__name__}")
    else:
        lines.append(f"- {k}: {repr(v)}")

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print("Done! Output written to scratch/inspect_detail_keys_output.txt")
