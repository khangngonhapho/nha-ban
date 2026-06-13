import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("scratch/page_body.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

text = soup.get_text()
print("=== All Text Content ===")
for line in text.split("\n"):
    line = line.strip()
    if line:
        print(line)

print("\n=== Elements Structure ===")
for el in soup.find_all(string=True):
    parent = el.parent
    if parent and parent.name in ["p", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6"]:
        t = el.strip()
        if t and len(t) > 2:
            print(f"[{parent.name}]: {t}")
