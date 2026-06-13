from bs4 import BeautifulSoup
import os

html_file = "Thien Khoi Group - Nguon Hang - Danh Sach.html"
if os.path.exists(html_file):
    try:
        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        
        # Look for table headers
        headers = [th.text.strip() for th in soup.select("table th")]
        print("Table Headers found:")
        for idx, h in enumerate(headers):
            print(f"  {idx+1}: {h}")
            
        # Inspect a single row (tr starting with tr_)
        row = soup.select_one("tr[id^='tr_']")
        if row:
            print("\nSample row cell texts:")
            cells = [td.text.strip() for td in row.select("td")]
            for idx, c in enumerate(cells):
                # Print first 50 chars of each cell text ascii-safely
                safe_c = ''.join(char if ord(char) < 128 else '?' for char in c)
                print(f"  Col {idx+1}: {safe_c[:80]}")
        else:
            print("\nNo rows starting with tr_ found in sample HTML.")
            
    except Exception as e:
        print("Error:", e)
else:
    print(f"File {html_file} does not exist.")
