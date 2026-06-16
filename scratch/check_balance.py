import sys

def check_balance(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    braces = []
    parentheses = []
    brackets = []
    
    in_string = False
    string_char = None
    escape = False
    in_comment = False
    comment_type = None  # 'single' or 'multi'
    
    i = 0
    while i < len(content):
        char = content[i]
        
        if escape:
            escape = False
            i += 1
            continue
            
        if char == '\\':
            escape = True
            i += 1
            continue
            
        if in_comment:
            if comment_type == 'single' and char == '\n':
                in_comment = False
            elif comment_type == 'multi' and char == '*' and i + 1 < len(content) and content[i+1] == '/':
                in_comment = False
                i += 1
            i += 1
            continue
            
        if in_string:
            if char == string_char:
                in_string = False
            i += 1
            continue
            
        # Check comments
        if char == '/' and i + 1 < len(content):
            if content[i+1] == '/':
                in_comment = True
                comment_type = 'single'
                i += 2
                continue
            elif content[i+1] == '*':
                in_comment = True
                comment_type = 'multi'
                i += 2
                continue
                
        if char in ["'", '"', '`']:
            in_string = True
            string_char = char
            i += 1
            continue
            
        if char == '{':
            braces.append(i)
        elif char == '}':
            if braces:
                braces.pop()
            else:
                print(f"Unmatched '}}' at index {i}, near: {content[max(0, i-50):i+50]}".encode('ascii', errors='replace').decode('ascii'))
        elif char == '(':
            parentheses.append(i)
        elif char == ')':
            if parentheses:
                parentheses.pop()
            else:
                print(f"Unmatched ')' at index {i}, near: {content[max(0, i-50):i+50]}".encode('ascii', errors='replace').decode('ascii'))
        elif char == '[':
            brackets.append(i)
        elif char == ']':
            if brackets:
                brackets.pop()
            else:
                print(f"Unmatched ']' at index {i}, near: {content[max(0, i-50):i+50]}".encode('ascii', errors='replace').decode('ascii'))
                
        i += 1
        
    print(f"Unbalanced braces count: {len(braces)}")
    for b in braces:
        line = content[:b].count('\n') + 1
        print(f"  Unmatched '{{' starting at line {line}: {content[b:b+40]}...".encode('ascii', errors='replace').decode('ascii'))
        
    print(f"Unbalanced parentheses count: {len(parentheses)}")
    for p in parentheses:
        line = content[:p].count('\n') + 1
        print(f"  Unmatched '(' starting at line {line}: {content[p:p+40]}...".encode('ascii', errors='replace').decode('ascii'))
        
    print(f"Unbalanced brackets count: {len(brackets)}")
    for br in brackets:
        line = content[:br].count('\n') + 1
        print(f"  Unmatched '[' starting at line {line}: {content[br:br+40]}...".encode('ascii', errors='replace').decode('ascii'))

if __name__ == '__main__':
    check_balance('static/js/lego_detail_admin.js')
