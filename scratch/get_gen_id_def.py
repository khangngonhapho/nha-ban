import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("pool_lego.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

printing = False
for i, line in enumerate(lines):
    if "def gen_id_khang_ngo_python" in line:
        printing = True
    if printing:
        print(f"Line {i+1}: {line.strip()}")
        if line.startswith("def ") and "gen_id_khang_ngo_python" not in line:
            printing = False
        if line.strip() == "" and i > 300: # safety break
            pass
        if len(line.strip()) > 0 and line.strip().startswith("# =================================================="):
            printing = False
