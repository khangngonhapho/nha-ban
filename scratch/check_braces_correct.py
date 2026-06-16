import sys

def check_js_syntax(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    stack = []
    mapping = {')': '(', ']': '[', '}': '{'}
    openers = set(mapping.values())
    closers = set(mapping.keys())

    in_string = None  # None, "'", '"', '`'
    in_comment = None  # None, '//', '/*'
    escaped = False

    line_num = 1
    char_num = 0

    for i, char in enumerate(content):
        if char == '\n':
            line_num += 1
            char_num = 0
        else:
            char_num += 1

        if in_comment == '//':
            if char == '\n':
                in_comment = None
            continue
        elif in_comment == '/*':
            if char == '/' and i > 0 and content[i-1] == '*':
                in_comment = None
            continue

        if in_string:
            if escaped:
                escaped = False
                continue
            if char == '\\':
                escaped = True
                continue
            if char == in_string:
                in_string = None
            continue

        # Check for comments start
        if char == '/' and i + 1 < len(content):
            next_char = content[i+1]
            if next_char == '/':
                in_comment = '//'
                continue
            elif next_char == '*':
                in_comment = '/*'
                continue

        # Check for strings start
        if char in ["'", '"', '`']:
            in_string = char
            escaped = False
            continue

        # Check for brackets
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
        print("Unmatched opening brackets left in stack:")
        for char, line, col in stack[:5]:
            print(f"  '{char}' at line {line}, char {col}")
        return False

    print("All brackets match perfectly!")
    return True

if __name__ == "__main__":
    check_js_syntax('static/js/lego_helpers.js')
