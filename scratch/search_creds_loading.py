with open("pool_lego.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "gspread" in line or "service_account" in line or "credentials" in line:
            print(f"Line {i+1}: {line.strip()}")
