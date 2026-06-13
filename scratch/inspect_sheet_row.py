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
    
    source_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
    try:
        ss = client.open_by_key(source_id)
        sheet = ss.worksheet("Source")
        
        # Get row 3
        row3 = sheet.row_values(3)
        print("Row 3 values:")
        for idx, val in enumerate(row3):
            print(f"Col {idx+1}: {val}")
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
