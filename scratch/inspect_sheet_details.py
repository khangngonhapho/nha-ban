import sys
import os
import json
import gspread

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    
    # 1. Inspect Source (v1)
    source_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
    print(f"--- INSPECTING SOURCE (v1) [ID: {source_id}] ---")
    try:
        ss = client.open_by_key(source_id)
        print("Worksheets:", [w.title for w in ss.worksheets()])
        sheet = ss.worksheet("Source")
        headers = sheet.row_values(1)
        print("Headers count:", len(headers))
        print("Sample headers:", headers[:15])
        
        # Look for Cloudinary links in a sample of rows
        all_vals = sheet.get_all_values()
        cld_count = 0
        for r_idx, r in enumerate(all_vals[1:], start=2):
            for c_idx, cell in enumerate(r, start=1):
                if "cloudinary.com" in cell:
                    cld_count += 1
        print("Found Cloudinary cells in Source sheet:", cld_count)
    except Exception as e:
        print("Error inspecting Source (v1):", e)
        
    # 2. Inspect Pool (v1)
    pool_id = "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0"
    print(f"\n--- INSPECTING POOL (v1) [ID: {pool_id}] ---")
    try:
        ss = client.open_by_key(pool_id)
        print("Worksheets:", [w.title for w in ss.worksheets()])
        sheet = ss.get_worksheet(0)
        print("First sheet title:", sheet.title)
        headers = sheet.row_values(1)
        print("Headers count:", len(headers))
        print("Sample headers:", headers[:15])
        
        # Look for Cloudinary links
        all_vals = sheet.get_all_values()
        cld_count = 0
        for r_idx, r in enumerate(all_vals[1:], start=2):
            for c_idx, cell in enumerate(r, start=1):
                if "cloudinary.com" in cell:
                    cld_count += 1
        print("Found Cloudinary cells in Pool (v1) sheet:", cld_count)
    except Exception as e:
        print("Error inspecting Pool (v1):", e)

if __name__ == '__main__':
    main()
