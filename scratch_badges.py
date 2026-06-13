import re
from bs4 import BeautifulSoup

def main():
    content = open('Thien Khoi Group - Nguon Hang - Chi Tiet New.html', encoding='utf-8').read()
    soup = BeautifulSoup(content, 'html.parser')
    
    out = open('badges_details.txt', 'w', encoding='utf-8')
    
    # Let's find elements with text "Hiếm" or "Chính chủ" or "Trường học" or "Bệnh viện"
    keywords = ["Hiếm", "Giấy phép xây dựng", "Phòng cháy cháy nổ", "Chính chủ", "Gần bệnh viện"]
    for keyword in keywords:
        matched = soup.find_all(string=re.compile(keyword, re.I))
        out.write(f"\nKeyword: {keyword} (Found {len(matched)})\n")
        for el in matched:
            parent = el.parent
            out.write(f"  Parent: <{parent.name} class={parent.get('class')} id={parent.get('id')}> text={repr(parent.text.strip())}\n")
            if parent.parent:
                out.write(f"    Grandparent: <{parent.parent.name} class={parent.parent.get('class')}> text={repr(parent.parent.text.strip())[:100]}\n")
                if parent.parent.parent:
                    out.write(f"      Great-grandparent: <{parent.parent.parent.name} class={parent.parent.parent.get('class')}>\n")
                    
    out.close()

if __name__ == '__main__':
    main()
