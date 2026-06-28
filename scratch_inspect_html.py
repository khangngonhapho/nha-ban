import sys
import re
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

def main():
    html_path = 'Thien Khoi Group - Nguon Hang - Huong Jun28.html'
    content = open(html_path, encoding='utf-8').read()
    soup = BeautifulSoup(content, 'html.parser')
    
    print("--- Heading Tags ---")
    for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        print(f"<{h.name}>: {repr(h.get_text().strip())}")
        
    print("\n--- Searching for 'Mã' in text ---")
    matches = soup.find_all(string=re.compile(r'mã', re.IGNORECASE))
    print(f"Found {len(matches)} occurrences containing 'mã'.")
    for i, m in enumerate(matches[:15]):
        print(f"  [{i}] {repr(m.strip())} -> Parent: <{m.parent.name}>")
        # print parent's text and siblings
        print(f"      Parent text: {repr(m.parent.get_text().strip())}")
        sibs = [s.get_text().strip() for s in m.parent.next_siblings if hasattr(s, 'get_text')]
        sibs = [s for s in sibs if s]
        print(f"      Siblings: {sibs[:3]}")

    print("\n--- Inspecting scripts containing JSON/data ---")
    # Sometimes Next.js pages have <script id="__NEXT_DATA__"> or similar
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("Found __NEXT_DATA__ script!")
        # Print a snippet of it (first 1000 chars)
        print(next_data.string[:1000])
        # Search for any ID-like fields inside it
        ids = re.findall(r'"id"\s*:\s*"([^"]+)"', next_data.string)
        print(f"Found IDs in NEXT_DATA: {list(set(ids))[:10]}")
        ma_hangs = re.findall(r'"Ma_Hang"\s*:\s*"([^"]+)"', next_data.string)
        print(f"Found Ma_Hang in NEXT_DATA: {list(set(ma_hangs))[:10]}")
        tk_ids = re.findall(r'"tk_id"\s*:\s*"([^"]+)"', next_data.string)
        print(f"Found tk_id in NEXT_DATA: {list(set(tk_ids))[:10]}")

if __name__ == '__main__':
    main()
