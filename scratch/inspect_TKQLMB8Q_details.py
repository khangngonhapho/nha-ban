import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("scratch/detail_TKQLMB8Q.json", "r", encoding="utf-8") as f:
    res = json.load(f)

data = res.get("data", {})

# Find where the phone number is located recursively
def find_value_in_json(obj, target_val, path="root"):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(v) == str(target_val):
                found.append(f"{path}.{k}")
            elif isinstance(v, (dict, list)):
                found.extend(find_value_in_json(v, target_val, f"{path}.{k}"))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            if str(item) == str(target_val):
                found.append(f"{path}[{idx}]")
            elif isinstance(item, (dict, list)):
                found.extend(find_value_in_json(item, target_val, f"{path}[{idx}]"))
    return found

paths = find_value_in_json(data, "0941151187")
print(f"Value '0941151187' found at paths: {paths}")

# Let's inspect ownerSideUser and homeOwner again
print("\n=== homeOwner inside detail_TKQLMB8Q.json ===")
print(json.dumps(data.get("homeOwner"), indent=2, ensure_ascii=False))

print("\n=== contactPhoneNumber/contactName ===")
print(f"contactName: {data.get('contactName')}")
print(f"contactPhoneNumber: {data.get('contactPhoneNumber')}")

print("\n=== checking criteria list ===")
criteria = data.get("criteria", [])
print(f"Total criteria items: {len(criteria)}")
