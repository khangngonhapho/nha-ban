import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read system_prompt.txt
with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\system_prompt.txt", "r", encoding="utf-8") as f:
    local_prompt = f.read().strip()

# Import manager to see its DEFAULT_CONFIG
sys.path.append("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo")
try:
    import manager
    manager_prompt = manager.DEFAULT_CONFIG["openai_system_prompt"].strip()
    
    import difflib
    diff = list(difflib.unified_diff(
        local_prompt.splitlines(),
        manager_prompt.splitlines(),
        fromfile='system_prompt.txt',
        tofile='manager.py DEFAULT_CONFIG',
        n=0
    ))
    print(f"Total diff lines: {len(diff)}")
    for line in diff:
        print(line)
except Exception as e:
    print(f"Error: {e}")
