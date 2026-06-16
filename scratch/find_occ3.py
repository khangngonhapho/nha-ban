import subprocess
import sys

def main():
    content = subprocess.check_output(
        ["git", "show", "HEAD:index.html"],
        cwd="d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    ).decode("utf-8")
    
    search_str = 'if (isAdmin && (p.original_row_data || p.isFromPoolOnly))'
    pos = 0
    for i in range(3):
        pos = content.find(search_str, pos)
        if pos == -1:
            print(f"Error: Could not find occurrence {i+1}")
            sys.exit(1)
        if i < 2:
            pos += len(search_str)
            
    # Now find the end of block
    from check_block import extract_js_block
    block = extract_js_block(content, pos)
    start_line = content[:pos].count('\n') + 1
    end_line = start_line + block.count('\n')
    print(f"Occurrence 3 starts at line {start_line} and ends at line {end_line}")
    print("First 200 chars:")
    print(block[:200])
    print("Last 200 chars:")
    print(block[-200:])

if __name__ == '__main__':
    main()
