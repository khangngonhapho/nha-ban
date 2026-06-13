import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("scratch/detail_Backend_Direct_ID.txt", "r", encoding="utf-8") as f:
    res = json.load(f)

data = res.get("data", {})

print("=== homeOwner details ===")
home_owners = data.get("homeOwner", [])
print(json.dumps(home_owners, indent=2, ensure_ascii=False))

print("\n=== sourceSenderUser details ===")
print(json.dumps(data.get("sourceSenderUser"), indent=2, ensure_ascii=False))

print("\n=== ownerSideUser details ===")
print(json.dumps(data.get("ownerSideUser"), indent=2, ensure_ascii=False))

print("\n=== checking media types ===")
media = data.get("media", [])
for idx, m in enumerate(media):
    print(f"[{idx+1}] type={m.get('type')} name={m.get('name')} filename={m.get('filename')}")
