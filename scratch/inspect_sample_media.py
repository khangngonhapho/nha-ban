import json

with open("scratch/sample_listing_list.json", "r", encoding="utf-8") as f:
    res = json.load(f)

listings = res.get("data", {}).get("data", [])
if listings:
    first = listings[0]
    media = first.get("media", [])
    print(f"Total media items: {len(media)}")
    if media:
        print("First media item structure:")
        print(json.dumps(media[0], indent=2, ensure_ascii=False))
        print("\nAll media URLs:")
        for idx, m in enumerate(media):
            print(f"  [{idx+1}] type={m.get('type')} url={m.get('url')}")
