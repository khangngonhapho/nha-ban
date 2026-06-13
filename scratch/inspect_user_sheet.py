import sys
sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager
import gspread

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    sheet_id = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    
    print(f"--- INSPECTING SHEET [ID: {sheet_id}] ---")
    try:
        ss = client.open_by_key(sheet_id)
        worksheets = ss.worksheets()
        print("Worksheets:", [w.title for w in worksheets])
        
        for w in worksheets:
            sheet = w
            all_vals = sheet.get_all_values()
            print(f"\nWorksheet '{sheet.title}':")
            print(f"  - Rows count: {len(all_vals)}")
            if len(all_vals) > 0:
                print(f"  - Cols count: {len(all_vals[0])}")
                
            # Count Cloudinary links
            cld_count = 0
            for r_idx, r in enumerate(all_vals):
                for c_idx, cell in enumerate(r):
                    if "cloudinary.com" in cell:
                        cld_count += 1
                        if cld_count <= 5:
                            print(f"    Sample match at Row {r_idx+1}, Col {c_idx+1}: {cell[:100]}")
            print(f"  - Cloudinary cells found: {cld_count}")
            
    except Exception as e:
        print("Error inspecting sheet:", e)

if __name__ == '__main__':
    main()
