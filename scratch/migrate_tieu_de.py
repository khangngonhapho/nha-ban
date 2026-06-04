import os
import sys
import argparse
import time

# Ensure imports from parent directory function correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials, load_config

def main():
    parser = argparse.ArgumentParser(description="Migrate misplaced Tiêu đề BDS to tieu_de column in Source sheet.")
    parser.add_argument("--write", action="store_true", help="Perform the actual write operation to Google Sheets")
    args = parser.parse_args()

    print("=========================================================")
    print("🔄 START MIGRATION: MISPLACED TITLES (Tiêu đề BDS -> tieu_de)")
    print(f"👉 Mode: {'WRITE (Actual Update)' if args.write else 'DRY RUN (Read Only)'}")
    print("=========================================================")

    creds = get_google_credentials()
    if not creds:
        print("[❌ ERROR] Google OAuth credentials not found!")
        return

    try:
        import gspread
        from gspread import Cell
    except ImportError:
        print("[❌ ERROR] gspread library not installed. Install via 'pip install gspread'")
        return

    source_sheet_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

    try:
        client = gspread.authorize(creds)
        print("  - Connecting to Google Sheets...")
        source_spreadsheet = client.open_by_key(source_sheet_id)
        source_sheet = source_spreadsheet.worksheet("Source")
        print("  - Reading Source worksheet values...")
        all_rows = source_sheet.get_all_values()
    except Exception as e:
        print(f"[❌ ERROR] Failed to connect or read from Google Sheet: {str(e)}")
        return

    if len(all_rows) < 3:
        print("[-] Sheet has no data rows to process.")
        return

    # Header is at index 1 (row 2). Data starts at row 3 (index 2).
    # Column E (tieu_de) is index 4 (col 5)
    # Column AN (Tiêu đề BDS) is index 39 (col 40)
    # Column D (id) is index 3 (col 4)
    # Column AH (ten_duong) or other columns for address identification
    
    cells_to_update = []
    affected_count = 0

    print("\n🔍 Scanning rows for misplaced titles...")
    for idx, row in enumerate(all_rows[2:], start=3):
        # Ensure row is long enough
        if len(row) < 40:
            continue
            
        sys_id = row[37].strip() if len(row) > 37 else ""
        kn_id = row[3].strip()     # Column D
        tieu_de_val = row[4].strip() # Column E
        tieu_de_bds_val = row[39].strip() # Column AN
        
        # If Column AN has a value, it means it was mis-saved here by the editor
        if tieu_de_bds_val:
            affected_count += 1
            print(f"  Row {idx} | ID: {kn_id or sys_id} | Current tieu_de: '{tieu_de_val}'")
            print(f"         └─ Misplaced title found: '{tieu_de_bds_val}'")
            
            if args.write:
                # We will copy it to tieu_de (Col 5) and clear Tiêu đề BDS (Col 40)
                cells_to_update.append(Cell(row=idx, col=5, value=tieu_de_bds_val))
                cells_to_update.append(Cell(row=idx, col=40, value=""))
                print(f"         └─ [QUEUED] Update E={tieu_de_bds_val}, AN=''")

    print(f"\n📊 Scan Complete: Found {affected_count} rows with misplaced titles.")

    if affected_count == 0:
        print("✨ No rows need migration. Everything looks correct!")
        return

    if not args.write:
        print("💡 This was a DRY RUN. No changes were made to the Google Sheet.")
        print("💡 Run with 'python scratch/migrate_tieu_de.py --write' to apply the changes.")
        return

    if cells_to_update:
        print(f"\n⚡ Applying {len(cells_to_update)} cell updates via batch_update...")
        try:
            source_sheet.update_cells(cells_to_update, value_input_option='USER_ENTERED')
            print("✅ Sheets updated successfully!")
        except Exception as e:
            print(f"[❌ ERROR] Failed to update Google Sheet: {str(e)}")

    print("=========================================================")
    print("🏁 MIGRATION COMPLETE")
    print("=========================================================")

if __name__ == "__main__":
    main()
