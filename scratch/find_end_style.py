with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if '</style>' in line:
        print(f"Found </style> at line {i+1}: {line.strip()}")
        # print 5 lines before
        start = max(0, i - 5)
        for j in range(start, i + 1):
            print(f"  {j+1}: {lines[j]}")
        break
