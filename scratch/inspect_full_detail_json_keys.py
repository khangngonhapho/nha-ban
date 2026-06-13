import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("scratch/detail_TKQLMB8Q.json", "r", encoding="utf-8") as f:
    res = json.load(f)

data = res.get("data", {})
print("=== Non-null keys and values in detail JSON ===")
for k, v in data.items():
    if v is not None and v != "" and v != [] and v != {}:
        if isinstance(v, str) and len(v) > 200:
            print(f"  {k}: str (len {len(v)})")
        elif isinstance(v, list):
            print(f"  {k}: list (len {len(v)})")
        elif isinstance(v, dict):
            print(f"  {k}: dict (len {len(v)})")
        else:
            print(f"  {k}: {repr(v)}")
