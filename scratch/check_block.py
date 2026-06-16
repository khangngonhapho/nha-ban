import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

def extract_js_block(content, start_pos):
    brace_start = content.find('{', start_pos)
    if brace_start == -1:
        return ""
    
    brace_count = 1
    i = brace_start + 1
    in_string = False
    string_char = None
    escape = False
    
    while i < len(content) and brace_count > 0:
        char = content[i]
        if escape:
            escape = False
            i += 1
            continue
        if char == '\\':
            escape = True
            i += 1
            continue
        if in_string:
            if char == string_char:
                in_string = False
            i += 1
            continue
        if char in ["'", '"', '`']:
            in_string = True
            string_char = char
            i += 1
            continue
            
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        
        i += 1
        
    return content[start_pos:i]

content = subprocess.check_output(
    ["git", "show", "HEAD:index.html"],
    cwd="d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
).decode("utf-8")

search_str = 'if (isAdmin && (p.original_row_data || p.isFromPoolOnly))'
pos = 0
occurrence = 1
while True:
    pos = content.find(search_str, pos)
    if pos == -1:
        break
    
    # Get line number
    line_num = content[:pos].count('\n') + 1
    block = extract_js_block(content, pos)
    print(f"Occurrence {occurrence} at line {line_num} (Length: {len(block)}):")
    print(block[:250])
    print("-" * 50)
    
    pos += len(search_str)
    occurrence += 1
