def check_sub_balance(filepath, start_line, end_line):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    sub_lines = lines[start_line-1:end_line]
    content = "".join(sub_lines)
    
    braces = 0
    parentheses = 0
    brackets = 0
    
    for idx, char in enumerate(content):
        if char == '{': braces += 1
        elif char == '}': braces -= 1
        elif char == '(': parentheses += 1
        elif char == ')': parentheses -= 1
        elif char == '[': brackets += 1
        elif char == ']': brackets -= 1
        
    print(f"Braces balance: {braces}")
    print(f"Parentheses balance: {parentheses}")
    print(f"Brackets balance: {brackets}")

def check_sub_balance_git():
    import subprocess
    content = subprocess.check_output(
        ["git", "show", "HEAD:index.html"],
        cwd="d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    ).decode("utf-8")
    lines = content.splitlines()
    sub_lines = lines[1865-1:2010]
    content_sub = "\n".join(sub_lines)
    
    braces = 0
    parentheses = 0
    brackets = 0
    
    for idx, char in enumerate(content_sub):
        if char == '{': braces += 1
        elif char == '}': braces -= 1
        elif char == '(': parentheses += 1
        elif char == ')': parentheses -= 1
        elif char == '[': brackets += 1
        elif char == ']': brackets -= 1
        
    print(f"Git HEAD post-render block braces balance: {braces}")
    print(f"Git HEAD post-render block parentheses balance: {parentheses}")
    print(f"Git HEAD post-render block brackets balance: {brackets}")

if __name__ == '__main__':
    check_sub_balance_git()
