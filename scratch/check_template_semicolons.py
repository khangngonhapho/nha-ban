import re

def check_semicolons(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find sbody.innerHTML = ` ... `;
    start_idx = content.find('sbody.innerHTML = `')
    if start_idx == -1:
        print("Could not find sbody.innerHTML")
        return
        
    # Find matching closing backtick for sbody.innerHTML
    # Since there are nested backticks, we need a brace/backtick tracker
    brace_count = 0
    in_expr = False
    i = start_idx + len('sbody.innerHTML = `')
    
    # We want to find all ${ ... } blocks and see if they contain ';'
    exprs = []
    
    while i < len(content):
        char = content[i]
        
        # Check if we hit the closing backtick of sbody.innerHTML
        # For simplicity, let's find all occurrences of ${ and trace them
        if content[i:i+2] == '${':
            # Trace expression
            start_expr = i
            braces = 1
            j = i + 2
            in_str = False
            str_char = None
            escape = False
            
            while j < len(content) and braces > 0:
                c = content[j]
                if escape:
                    escape = False
                    j += 1
                    continue
                if c == '\\':
                    escape = True
                    j += 1
                    continue
                if in_str:
                    if c == str_char:
                        in_str = False
                    j += 1
                    continue
                if c in ["'", '"', '`']:
                    in_str = True
                    str_char = c
                    j += 1
                    continue
                if c == '{':
                    braces += 1
                elif c == '}':
                    braces -= 1
                j += 1
            
            expr_text = content[start_expr:j]
            if ';' in expr_text:
                line_num = content[:start_expr].count('\n') + 1
                msg = f"Line {line_num}: Expression contains semicolon: {expr_text.strip()}"
                print(msg.encode('ascii', errors='replace').decode('ascii'))
            
            i = j
            continue
            
        i += 1

if __name__ == '__main__':
    check_semicolons('static/js/lego_detail_admin.js')
