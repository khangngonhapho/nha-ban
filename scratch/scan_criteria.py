import os
import json
import re

scratch_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch"
group_codes = {}

for fn in os.listdir(scratch_dir):
    fp = os.path.join(scratch_dir, fn)
    if fn.endswith('.json'):
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            def find_criteria(obj):
                if isinstance(obj, dict):
                    if "groupCode" in obj and "groupName" in obj:
                        code = obj["groupCode"]
                        name = obj["groupName"]
                        if code not in group_codes:
                            group_codes[code] = {"name": name, "values": set()}
                        if "name" in obj:
                            group_codes[code]["values"].add(obj["name"])
                    for v in obj.values():
                        find_criteria(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_criteria(item)

            find_criteria(data)
        except Exception as e:
            pass

lines = []
for code, info in group_codes.items():
    vals = list(info["values"])
    lines.append(f"Code: {code} ({info['name']})")
    lines.append(f"  Values: {', '.join(vals[:10])}")
    lines.append("")

out_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/scan_criteria_output.txt"
with open(out_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print("Done! Written to scratch/scan_criteria_output.txt")
