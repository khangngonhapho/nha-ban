import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ids = [
    "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0",
    "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE",
    "1JbCyE6peGBcsH8EUhlqdwPwDH9k3wwR6Sog9-pBflc4",
    "14qsVxa4l3m_J4DiJg4V0ZRGxjiHtNNAhD9sauhRguiU",
    "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
]

with open('SOURCE_OF_TRUTH.md', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    for i in ids:
        if i in line:
            print(f"Line {idx+1}: {line.strip()}")
