import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("scratch/sample_listing_list.json", "r", encoding="utf-8") as f:
    res = json.load(f)

listings = res.get("data", {}).get("data", [])
print(f"Total listings: {len(listings)}")

if listings:
    first = listings[0]
    print("\nKeys in listing:")
    print(list(first.keys()))
    
    print("\nSample values of first listing:")
    for k, v in first.items():
        if isinstance(v, (dict, list)):
            print(f"  {k}: {type(v).__name__} (len {len(v)})")
        else:
            print(f"  {k}: {repr(v)}")
            
    # Let's print nested objects
    print("\nNested 'street':", first.get("street"))
    print("Nested 'criteria':", first.get("criteria"))
    print("Nested 'district':", first.get("district"))
    print("Nested 'ward':", first.get("ward"))
    print("Nested 'ownerSideUser':", first.get("ownerSideUser"))
    print("Nested 'createdByUser':", first.get("createdByUser"))
