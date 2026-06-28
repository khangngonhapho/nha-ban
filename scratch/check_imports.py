with open("pool_lego.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("import ") or "import " in line or "from " in line:
            print(line.strip())
