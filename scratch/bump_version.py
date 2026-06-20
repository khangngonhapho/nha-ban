import re
import time
import os

def main():
    html_path = 'index.html'
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return 1
        
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Generate new version based on current local time
    # Format: YYYYMMDDHHMM
    new_version = time.strftime('%Y%m%d%H%M', time.localtime())
    print(f"New cache-busting version: {new_version}")
    
    # Regex to find ?v=digits or &v=digits inside static links in head
    # Examples:
    # /static/css/global.css?v=202606201715
    # /static/js/lego_core.js?v=202606201715
    pattern = r'(\/static\/(?:css|js)\/[\w_.-]+(?:\.css|\.js))\?v=\d+'
    
    # Check if there is any match
    matches = re.findall(pattern, content)
    if not matches:
        print("No version parameters found in index.html to update.")
        return 0
        
    updated_content = re.sub(pattern, rf'\1?v={new_version}', content)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
        
    print(f"Successfully updated cache-busting version in {html_path} for {len(matches)} files.")
    return 0

if __name__ == '__main__':
    exit(main())
