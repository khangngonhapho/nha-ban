import sqlite3
import os

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get columns
    c.execute("PRAGMA table_info(listings)")
    cols = [col[1] for col in c.fetchall()]
    
    # We want to check columns containing URLs
    image_cols = [
        "Hinh_Nhan_Dien", "So_do_thua_dat_1", "So_do_thua_dat_2", "So_do_thua_dat_3", "So_do_thua_dat_4", "So_do_thua_dat_5",
        "Hinh_Mat_Tien", "Hinh_Hem_1", "Hinh_Hem_2", "Hinh_Hem_3", "Hinh_Hem_4", "Hinh_Hem_5",
        "Hinh_Hem_6", "Hinh_Hem_7", "Hinh_Hem_8", "Hinh_Hem_9", "Hinh_Hem_10",
        "Anh_1", "Anh_2", "Anh_3", "Anh_4", "Anh_5", "Anh_6", "Anh_7", "Anh_8", "Anh_9", "Anh_10",
        "Anh_Public_VD_1_3_5", "Anh_Hem_Public_VD_1_2"
    ]
    
    # Find active ones
    active_cols = [col for col in image_cols if col in cols]
    print(f"Checking columns: {active_cols}")
    
    total_listings = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    print(f"Total listings: {total_listings}")
    
    # Let's count how many listings have at least one cloudinary URL, and total occurrences
    cld_counts = {}
    total_cloudinary_links = 0
    all_cloudinary_urls = set()
    
    # Let's query rows
    c.execute(f"SELECT id, tk_id, {', '.join(active_cols)} FROM listings")
    rows = c.fetchall()
    
    listings_with_cld = 0
    for r in rows:
        lid = r[0]
        tk_id = r[1]
        has_cld = False
        for idx, col_val in enumerate(r[2:]):
            col_name = active_cols[idx]
            if col_val and "cloudinary.com" in str(col_val):
                has_cld = True
                total_cloudinary_links += 1
                all_cloudinary_urls.add(str(col_val))
                cld_counts[col_name] = cld_counts.get(col_name, 0) + 1
        if has_cld:
            listings_with_cld += 1
            
    print(f"\nListings with at least one Cloudinary URL: {listings_with_cld}")
    print(f"Total Cloudinary links found: {total_cloudinary_links}")
    print(f"Unique Cloudinary URLs: {len(all_cloudinary_urls)}")
    print("\nBreakdown by column:")
    for col, cnt in sorted(cld_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col}: {cnt}")
        
    # Sample Cloudinary URLs
    print("\nSample Cloudinary URLs in database (up to 5):")
    for u in list(all_cloudinary_urls)[:5]:
        print(f"  {u}")
        
    conn.close()
else:
    print("DB not found")
