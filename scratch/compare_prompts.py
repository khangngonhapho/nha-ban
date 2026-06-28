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
    if local_prompt == manager_prompt:
        print("Prompts are identical!")
    else:
        print("Prompts differ! Let's print lengths:")
        print(f"system_prompt.txt length: {len(local_prompt)}")
        print(f"manager.py DEFAULT_CONFIG length: {len(manager_prompt)}")
        
        # Print differences
        import difflib
        diff = list(difflib.unified_diff(
            local_prompt.splitlines(),
            manager_prompt.splitlines(),
            fromfile='system_prompt.txt',
            tofile='manager.py DEFAULT_CONFIG'
        ))
        print("\n".join(diff[:20]))
except Exception as e:
    print(f"Error: {e}")
