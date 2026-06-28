import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

sid = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

try:
    gc = gspread.service_account(filename='credentials.json')
    print("Google Sheets Authenticated Successfully")
except Exception as e:
    print(f"Auth failed: {e}")
    sys.exit(1)

print(f"\nChecking Sheet: BDS_KhangNgo_Source (ID: {sid})")
try:
    sh = gc.open_by_key(sid)
    print(f"  Title: {sh.title}")
    worksheets = sh.worksheets()
    print(f"  Tabs: {[w.title for w in worksheets]}")
    
    for w in worksheets:
        data = w.get_all_values()
        if not data:
            print(f"    Tab '{w.title}': Empty")
            continue
        
        total_rows = len(data)
        tk_code_count = 0
        old_link_count = 0
        for r_idx, row in enumerate(data):
            row_str = " ".join(str(cell) for cell in row)
            # Check if any cell starts with 'TK-' or if first cell starts with 'TK-'
            # In source sheet, is 'System ID' the one starting with TK-?
            # Let's inspect where 'TK-' or 'data.thienkhoi.com' appears.
            if len(row) > 0 and str(row[0]).startswith("TK-"):
                tk_code_count += 1
            # Let's also check if 'TK-' appears anywhere in the row
            any_tk_code = any(str(cell).startswith("TK-") for cell in row)
            if any_tk_code:
                # print some samples
                pass
            if "data.thienkhoi.com" in row_str:
                old_link_count += 1
                
        print(f"    Tab '{w.title}': {total_rows} rows, {tk_code_count} rows starting with 'TK-', {old_link_count} rows containing old Link_Goc")
        
        # Let's print headers of the Source tab
        if w.title == "Source":
            print(f"    Source Headers: {data[0][:15]} ... (+ {len(data[0])-15} more)")
            # Let's count rows having 'TK-' in ANY cell
            any_tk_count = sum(1 for row in data if any(str(cell).startswith("TK-") or "TK-" in str(cell) for cell in row))
            print(f"    Source rows with 'TK-' anywhere: {any_tk_count}")
            # Print a few rows that have TK- or data.thienkhoi.com
            printed = 0
            for idx, row in enumerate(data):
                row_str = " ".join(str(cell) for cell in row)
                if ("TK-" in row_str or "data.thienkhoi.com" in row_str) and printed < 3:
                    print(f"      Sample Row {idx+1}: {row[:10]} ...")
                    printed += 1
                    
except Exception as e:
    print(f"  Error: {e}")
