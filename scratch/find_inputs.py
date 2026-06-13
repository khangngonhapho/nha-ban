import re, sys

sys.stdout.reconfigure(encoding='utf-8')
content = open('index.html', encoding='utf-8').read()

# Find all <input>, <select>, <textarea> elements
inputs = re.findall(r'<input\s+[^>]*>', content)
selects = re.findall(r'<select\s+[^>]*>', content)
textareas = re.findall(r'<textarea\s+[^>]*>', content)

print(f"Total <input> elements: {len(inputs)}")
for idx, inp in enumerate(inputs[:25]):
    # extract id if exists
    id_match = re.search(r'id=["\']([^"\']+)["\']', inp)
    id_str = id_match.group(1) if id_match else 'No ID'
    print(f"  {idx+1}. {id_str} ({inp[:70]}...)")

print(f"\nTotal <select> elements: {len(selects)}")
for idx, sel in enumerate(selects):
    id_match = re.search(r'id=["\']([^"\']+)["\']', sel)
    id_str = id_match.group(1) if id_match else 'No ID'
    print(f"  {idx+1}. {id_str} ({sel[:70]}...)")

print(f"\nTotal <textarea> elements: {len(textareas)}")
for idx, ta in enumerate(textareas):
    id_match = re.search(r'id=["\']([^"\']+)["\']', ta)
    id_str = id_match.group(1) if id_match else 'No ID'
    print(f"  {idx+1}. {ta[:70]}...")
