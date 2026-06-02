import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("curator.html", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("function setSidebarStatus")
if idx != -1:
    print("=================== setSidebarStatus Occurrences ===================")
    print(content[idx-100:idx+1500])
else:
    print("Could not find setSidebarStatus definition")
