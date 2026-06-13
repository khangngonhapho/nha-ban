import sys
import gspread

sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    sheet_id = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    
    ss = client.open_by_key(sheet_id)
    sheet = ss.worksheet("Pool")
    all_rows = sheet.get_all_values()
    
    col_map_keys = [
        1, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
        40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54,
        80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92
    ]
    
    json_cells = 0
    total_cloudinary_in_json = 0
    total_cloudinary_in_single = 0
    
    for r_idx, row in enumerate(all_rows[1:], start=2):
        for col_idx in col_map_keys:
            if col_idx < len(row):
                cell_val = row[col_idx].strip()
                if cell_val.startswith("["):
                    json_cells += 1
                    if "cloudinary.com" in cell_val:
                        total_cloudinary_in_json += 1
                else:
                    if "cloudinary.com" in cell_val:
                        total_cloudinary_in_single += 1
                        
    print(f"Total cells starting with '[' in image columns: {json_cells}")
    print(f"Cloudinary cells in JSON format: {total_cloudinary_in_json}")
    print(f"Cloudinary cells in Single URL format: {total_cloudinary_in_single}")

if __name__ == '__main__':
    main()
