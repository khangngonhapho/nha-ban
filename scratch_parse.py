import re
from bs4 import BeautifulSoup

def main():
    content = open('Thien Khoi Group - Nguon Hang - Chi Tiet New.html', encoding='utf-8').read()
    soup = BeautifulSoup(content, 'html.parser')
    
    out = open('extracted_details.txt', 'w', encoding='utf-8')
    
    # Let's find any text containing "Thông tin chi tiết"
    target = soup.find(string=re.compile('Thông tin chi tiết', re.I))
    out.write(f"Found target: {repr(target)}\n")
    
    if target:
        # Let's print all parents of target
        curr = target.parent
        out.write("Parents chain:\n")
        while curr:
            out.write(f"  {curr.name} class={curr.get('class')} id={curr.get('id')}\n")
            curr = curr.parent
            
        # Let's find all text nodes in the document that contain numbers or some labels
        # Let's also print all elements that have text inside
        # We can look for key words like "Độ rộng", "Đường trước nhà", "mặt thoáng"
        out.write("\n--- Searching for technical labels ---\n")
        keywords = ["mặt thoáng", "rộng", "đường trước", "bãi đỗ", "ô tô", "tiêu chí", "tiện ích", "hiếm", "trường học", "bệnh viện"]
        for el in soup.find_all(string=True):
            txt = el.strip()
            if any(k in txt.lower() for k in keywords):
                out.write(f"Text: {txt}\n  Parent: {el.parent.name} class={el.parent.get('class')} id={el.parent.get('id')}\n")
                if el.parent:
                    out.write(f"  Parent text content: {el.parent.text.strip()}\n")
                    # print siblings
                    sibs = list(el.parent.next_siblings)
                    out.write(f"  Siblings: {[s.text.strip() for s in sibs if getattr(s, 'text', '').strip()][:5]}\n")
                    
    out.close()

if __name__ == '__main__':
    main()
