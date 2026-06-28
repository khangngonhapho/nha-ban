import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

def main():
    html_path = 'Thien Khoi Group - Nguon Hang - Huong Jun28.html'
    content = open(html_path, encoding='utf-8').read()
    soup = BeautifulSoup(content, 'html.parser')
    
    # Let's search for "Hướng nhà" text and see its siblings and parent tree
    for p in soup.find_all(string=lambda text: text and "Hướng nhà" in text):
        parent = p.parent
        print(f"Found tag: <{parent.name} class={parent.get('class')}> with text {repr(p.strip())}")
        
        # print full parent element HTML
        print(f"Parent HTML: {parent}")
        
        # print grandparent
        grandparent = parent.parent
        if grandparent:
            print(f"Grandparent tag: <{grandparent.name} class={grandparent.get('class')}>")
            # print siblings of parent tag
            for idx, sib in enumerate(parent.next_siblings):
                if sib.name or sib.strip():
                    print(f"  Sibling {idx}: {repr(sib)} (type: {type(sib)})")
                    if hasattr(sib, 'get_text'):
                        print(f"    Sibling text: {repr(sib.get_text().strip())}")
            print(f"Grandparent full text: {repr(grandparent.get_text().strip())}")

if __name__ == '__main__':
    main()
