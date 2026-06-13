import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/index_styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Search for any > selector under .filter-panel or filterPanel
import re
matches = re.findall(r'\.filter-panel\s*>[^{]+{', css)
print("Matches for .filter-panel > :", matches)
matches2 = re.findall(r'#filterPanel\s*>[^{]+{', css)
print("Matches for #filterPanel > :", matches2)
