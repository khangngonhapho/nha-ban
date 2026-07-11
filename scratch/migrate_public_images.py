import os
import sys
import json
import sqlite3
import re

# Add root folder to path to load settings.json
sys.path.append(r'd:\LHTBrain\01_PROJECTS\BDS-KhangNgo')

def migrate_images():
    db_file = r'd:\LHTBrain\01_PROJECTS\BDS-KhangNgo\raw_archive_staging.db'
    if not os.path.exists(db_file):
        print(f"Staging database {db_file} not found!")
        return

    # Load configuration
    cfg = {}
    config_file = r'd:\LHTBrain\01_PROJECTS\BDS-KhangNgo\settings.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            cfg = json.load(f)

    r2_public_url = cfg.get("r2_public_url", "")
    print(f"R2 Public URL: {r2_public_url}")

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM listings")
    total_listings = cursor.fetchone()[0]
    print(f"Total listings to migrate: {total_listings}")

    # Read all listings
    cursor.execute("SELECT * FROM listings")
    listings = cursor.fetchall()

    processed_count = 0
    images_records_count = 0

    for listing in listings:
        tk_id = listing["tk_id"]
        system_id = listing["System_ID"] or ""
        
        # Load images_mapping_json if exists
        images_mapping = {}
        if listing["images_mapping_json"]:
            try:
                images_mapping = json.loads(listing["images_mapping_json"])
            except Exception:
                pass

        # Reverse map from R2 url to original URL
        r2_to_orig = {v: k for k, v in images_mapping.items() if v}

        migrated_images = []
        seen_urls = set()

        # Helper to add image
        def add_image(url, role, base_seq):
            if not url or not url.strip():
                return
            url = url.strip()
            # Normalize url if it's double wrapped or escaped
            url = url.replace('"', '').replace("'", "")
            if url in seen_urls:
                return
            seen_urls.add(url)

            # Determine origin
            # If filename contains SYS-, it is manually uploaded (origin='self')
            filename = os.path.basename(url)
            origin = "crawl"
            if "SYS-" in filename:
                origin = "self"

            # Determine image_url vs r2_url
            is_r2 = False
            if r2_public_url and r2_public_url in url:
                is_r2 = True
            elif "r2.dev" in url or "r2.cloudflarestorage.com" in url:
                is_r2 = True

            if is_r2:
                r2_url = url
                # Try to look up original TK URL
                image_url = r2_to_orig.get(r2_url, r2_url)
            else:
                image_url = url
                # Check if this URL is mapped to an R2 URL in mapping
                r2_url = images_mapping.get(image_url, None)

            migrated_images.append({
                "image_url": image_url,
                "r2_url": r2_url,
                "role": role,
                "sequence_index": len(migrated_images),
                "origin": origin,
                "is_hidden": 0
            })

        # 1. Migrate facade (Hinh_Mat_Tien)
        if listing["Hinh_Mat_Tien"]:
            add_image(listing["Hinh_Mat_Tien"], "facade", 0)

        # 2. Migrate diagrams (So_do_thua_dat_1 to So_do_thua_dat_5)
        for i in range(1, 6):
            col_name = f"So_do_thua_dat_{i}"
            if col_name in listing.keys() and listing[col_name]:
                add_image(listing[col_name], "diagram", i)

        # 3. Migrate alleys (Hinh_Hem_1 to Hinh_Hem_10)
        for i in range(1, 11):
            col_name = f"Hinh_Hem_{i}"
            if col_name in listing.keys() and listing[col_name]:
                add_image(listing[col_name], "alley", i)

        # 4. Migrate interiors (Anh_1 to Anh_25)
        for i in range(1, 26):
            col_name = f"Anh_{i}"
            if col_name in listing.keys() and listing[col_name]:
                add_image(listing[col_name], "interior", i)

        # Insert into listings_images
        for img in migrated_images:
            cursor.execute("""
                INSERT INTO listings_images (tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tk_id,
                system_id,
                img["image_url"],
                img["r2_url"],
                img["role"],
                img["sequence_index"],
                img["origin"],
                img["is_hidden"]
            ))
            images_records_count += 1

        # Compile JSONs
        # images_admin_json: all migrated images with metadata
        images_admin_json_str = json.dumps(migrated_images, ensure_ascii=False)

        # images_public_json: only visible, public images (interior, alley, background), sorted by sequence_index
        public_roles = {"interior", "alley", "background"}
        public_urls = [
            img["r2_url"] if img["r2_url"] else img["image_url"]
            for img in migrated_images
            if img["role"] in public_roles and img["is_hidden"] == 0
        ]
        images_public_json_str = json.dumps(public_urls, ensure_ascii=False)

        # Update listings table
        cursor.execute("""
            UPDATE listings
            SET images_admin_json = ?, images_public_json = ?
            WHERE tk_id = ?
        """, (images_admin_json_str, images_public_json_str, tk_id))

        processed_count += 1

    conn.commit()
    conn.close()

    print("Migration finished:")
    print(f"Processed listings: {processed_count} / {total_listings}")
    print(f"Inserted image records: {images_records_count}")

if __name__ == "__main__":
    migrate_images()
