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
    
    # Get values of row 4, columns 28 and 30
    row4 = sheet.row_values(4)
    print("Col 28 (Index 27):", row4[27] if len(row4) > 27 else "N/A")
    print("Col 30 (Index 29):", row4[29] if len(row4) > 29 else "N/A")
    print("Col 2 (Index 1):", row4[1] if len(row4) > 1 else "N/A")
    print("Col 74 (Index 73):", row4[73] if len(row4) > 73 else "N/A")

if __name__ == '__main__':
    main()
