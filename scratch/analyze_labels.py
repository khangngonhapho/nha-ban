import sys
from bs4 import BeautifulSoup

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path = r'D:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Thien Khoi Group - Nguon Hang - Chi Tiet New.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all elements that look like property labels or grid items
    # Typically, class contains 'text-grayscale-500' or similar
    print("Listing all text-grayscale-500 elements and their next siblings:")
    elements = soup.find_all(class_=lambda x: x and 'text-grayscale-500' in x)
    for idx, el in enumerate(elements):
        text = el.get_text().strip()
        sibling = el.find_next_sibling()
        sibling_text = sibling.get_text().strip() if sibling else "No sibling"
        print(f"  {idx}: label='{text}' -> value='{sibling_text}'")

if __name__ == '__main__':
    main()
