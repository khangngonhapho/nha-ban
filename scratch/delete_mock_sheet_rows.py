import os
import sys
import gspread

# Ensure we can import manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
import manager

def delete_mock_rows():
    cfg = manager.load_config()
    creds = manager.get_google_credentials()
    if not creds:
        print("Error: Could not load Google credentials.")
        return
        
    client = gspread.authorize(creds)
    client.http_client.session.timeout = 60
    
    # Staging Pool Sheet ID
    sheet_id = "1Nc8OwSHwacvuuS4blI8U9BrDOlVx6S6u9fU3AaKBYdY"
    print(f"Connecting to Staging Google Sheet: {sheet_id}...")
    ss = client.open_by_key(sheet_id)
    
    # 1. Delete from Pool tab
    print("\nProcessing 'Pool' tab...")
    pool_sheet = ss.worksheet("Pool")
    
    # Verify row 1248 has Nguyễn Huệ / TEST-MA-HANG
    row_1248 = pool_sheet.row_values(1248)
    row_str = " ".join(row_1248)
    print(f"  Row 1248 content: {row_1248[:10]}")
    
    if "Nguyễn Huệ" in row_str or "TEST-MA-HANG" in row_str or "Mock Title Text" in row_str:
        print("  Confirmed Nguyễn Huệ. Deleting row 1248...")
        pool_sheet.delete_rows(1248)
        print("  Row 1248 deleted successfully.")
    else:
        print("  Warning: Row 1248 does not match Nguyễn Huệ. Skipping deletion.")

    # 2. Delete from Pool_Images tab
    print("\nProcessing 'Pool_Images' tab...")
    images_sheet = ss.worksheet("Pool_Images")
    
    # Verify rows 2492 and 2493
    row_2493 = images_sheet.row_values(2493)
    row_2492 = images_sheet.row_values(2492)
    print(f"  Row 2492 content: {row_2492[:5]}")
    print(f"  Row 2493 content: {row_2493[:5]}")
    
    # Delete in reverse order
    if "test-tk-id-123" in " ".join(row_2493):
        print("  Deleting row 2493...")
        images_sheet.delete_rows(2493)
        print("  Row 2493 deleted successfully.")
        
    if "test-tk-id-123" in " ".join(row_2492):
        print("  Deleting row 2492...")
        images_sheet.delete_rows(2492)
        print("  Row 2492 deleted successfully.")
        
    print("\n=== GOOGLE SHEET CLEANUP COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    delete_mock_rows()
