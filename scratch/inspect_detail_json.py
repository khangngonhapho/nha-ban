import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("scratch/detail_Backend_Direct_ID.txt", "r", encoding="utf-8") as f:
    res = json.load(f)

data = res.get("data", {})
print("=== Root Keys in Detail JSON ===")
print(list(data.keys()))

# Check for description
print("\nDescription (mô tả):")
print(data.get("description"))

# Check for contact / landlord details
print("\nLandlord / Owner / Contact Details:")
print(f"contactName: {data.get('contactName')}")
print(f"contactPhoneNumber: {data.get('contactPhoneNumber')}")
print(f"ownerMobile: {data.get('ownerMobile')}")
print(f"ownerName: {data.get('ownerName')}")
print(f"ownerPhone: {data.get('ownerPhone')}")
print(f"ownerPhoneNumber: {data.get('ownerPhoneNumber')}")

# Print any fields starting with owner or landlord or contact
owner_fields = {k: v for k, v in data.items() if any(term in k.lower() for term in ["owner", "contact", "landlord", "phone", "mobile"])}
print("\nOwner/Contact-related fields found in JSON:")
print(json.dumps(owner_fields, indent=2, ensure_ascii=False))

# Print first few elements of media
media = data.get("media", [])
print(f"\nTotal media items in detail: {len(media)}")
for idx, m in enumerate(media[:5]):
    print(f"  [{idx+1}] type={m.get('type')} url={m.get('url')}")
