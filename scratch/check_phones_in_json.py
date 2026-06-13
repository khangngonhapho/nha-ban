import json

with open("scratch/detail_Backend_Direct_ID.txt", "r", encoding="utf-8") as f:
    content = f.read()

print("Contains 0941151187:", "0941151187" in content)
print("Contains 0944666655:", "0944666655" in content)
