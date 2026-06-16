import subprocess
import difflib

def main():
    # Get git HEAD lines
    content = subprocess.check_output(
        ["git", "show", "HEAD:index.html"],
        cwd="d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    ).decode("utf-8")
    lines_git = content.splitlines()[1865-1:2010]
    
    # Get generated file lines
    with open('static/js/lego_detail_admin.js', 'r', encoding='utf-8') as f:
        lines_gen = f.readlines()[362-1:508]
        
    lines_gen = [l.rstrip('\n') for l in lines_gen]
    
    diff = list(difflib.unified_diff(lines_git, lines_gen, fromfile='git_head', tofile='gen_file', lineterm=''))
    print('\n'.join(diff))

if __name__ == '__main__':
    main()
