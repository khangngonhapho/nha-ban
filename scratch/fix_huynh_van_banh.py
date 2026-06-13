import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def fix_hvb():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    print("[1/2] Kết nối và mở Source sheet...")
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    
    # Cột AL (cột 38) là System ID. Dòng 100
    col_letter = gspread.utils.rowcol_to_a1(100, 38).split("100")[0]
    print(f"  - Cập nhật System ID của dòng 100 thành 'SYS-MP75ES0J-9K' tại cột {col_letter}100...")
    source_sheet.update(range_name=f"{col_letter}100", values=[["SYS-MP75ES0J-9K"]])
    
    print("[✅] Đã cập nhật thành công!")

if __name__ == "__main__":
    fix_hvb()
