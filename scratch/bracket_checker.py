def check_brackets(filepath):
    content = open(filepath, encoding='utf-8').read()
    
    # Strip comments and strings to avoid matching brackets inside them
    # Simple regex-based strip
    import re
    # Strip multi-line comments /* ... */
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Strip single line comments // ...
    content = re.sub(r'//.*', '', content)
    # Strip string literals "..." and '...' and `...`
    # Replace with empty string but be careful with backslashes
    content = re.sub(r'"(?:[^"\\]|\\.)*"', '""', content)
    content = re.sub(r"'(?:[^'\\]|\\.)*'", "''", content)
    content = re.sub(r"`(?:[^`\\]|\\.)*`", "``", content)
    
    stack = []
    mapping = {')': '(', ']': '[', '}': '{'}
    openers = set(mapping.values())
    closers = set(mapping.keys())
    
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for char_num, char in enumerate(line, 1):
            if char in openers:
                stack.append((char, line_num, char_num))
            elif char in closers:
                if not stack:
                    print(f"Unmatched closing '{char}' at line {line_num}, char {char_num}")
                    return False
                top_char, top_line, top_char_num = stack.pop()
                if top_char != mapping[char]:
                    print(f"Mismatch: '{char}' at line {line_num}, char {char_num} does not match '{top_char}' from line {top_line}, char {top_char_num}")
                    return False
                    
    if stack:
        print(f"Unmatched opening brackets left in stack:")
        for char, line_num, char_num in stack[:5]:
            print(f"  '{char}' at line {line_num}, char {char_num}")
        return False
        
    print("All bracket pairs match perfectly!")
    return True

if __name__ == '__main__':
    # Re-run extraction first
    import os
    os.system('python scratch/extract_js.py')
    check_brackets('scratch/index_extracted.js')
