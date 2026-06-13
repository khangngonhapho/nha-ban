import re
from bs4 import BeautifulSoup

def main():
    content = open('Thien Khoi Group - Nguon Hang - Chi Tiet New.html', encoding='utf-8').read()
    soup = BeautifulSoup(content, 'html.parser')
    
    out = open('all_matched_texts.txt', 'w', encoding='utf-8')
    
    # Let's print out all divs/spans that contain text and their text content
    out.write("Searching for all divs/spans:\n")
    for el in soup.find_all(['div', 'span', 'p', 'button', 'li']):
        text = el.text.strip()
        if not text:
            continue
        # If the element has kids, only print if text is short or specific keywords
        if len(text) < 100 or any(k in text.lower() for k in ["thoáng", "mặt", "sau nhà", "bên cạnh", "ô tô", "đỗ xe"]):
            out.write(f"<{el.name} class={el.get('class')}> text={repr(text)}\n")
            
    out.close()

if __name__ == '__main__':
    main()
