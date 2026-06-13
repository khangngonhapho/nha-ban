import os

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/detail_Next_js_RSC_Detail_Page.txt"

if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print("Contains 0941151187:", "0941151187" in content)
    print("Contains 0944666655:", "0944666655" in content)
else:
    print("File not found")
