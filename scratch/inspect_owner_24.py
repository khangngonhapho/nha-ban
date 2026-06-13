import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("scratch/detail_TKQLMB8Q.json", "r", encoding="utf-8") as f:
    res = json.load(f)

data = res.get("data", {})
print("ownerSideUser:")
print(json.dumps(data.get("ownerSideUser"), indent=2, ensure_ascii=False))

print("\nHomeOwner Name:")
print(data.get("homeOwner"))
