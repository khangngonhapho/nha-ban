import sys
sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager
import gspread

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def main():
    creds = manager.get_google_credentials()
    if not creds:
        return
        
    client = gspread.authorize(creds)
    source_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
    
    ss = client.open_by_key(source_id)
    sheet = ss.worksheet("Source")
    all_rows = sheet.get_all_values()
    
    print("--- REMAINING CLOUDINARY CELLS ---")
    count = 0
    for r_idx, row in enumerate(all_rows[2:], start=3):
        ma_kn = row[3] if len(row) > 3 else ""
        sys_id = row[37] if len(row) > 37 else ""
        for c_idx, val in enumerate(row):
            if "cloudinary.com" in val:
                count += 1
                if count <= 40:
                    print(f"Row {r_idx} | Col {c_idx+1} | Ma KN: {ma_kn} | Sys ID: {sys_id} | Val: {val[:100]}")
                    
    print(f"Total remaining cells: {count}")

if __name__ == '__main__':
    main()
