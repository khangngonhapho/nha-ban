import re
import datetime
import os

def bump_html_versions():
    html_path = "index.html"
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return False
        
    # Generate timestamp in format YYYYMMDDHHMMSS (or YYYYMMDDHHMM)
    # Using local time or UTC. Let's use current time
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    print(f"Generating new version timestamp: {timestamp}")
    
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Match ?v= followed by digits
    pattern = r"(\?v=)\d+"
    
    # Check if there are any matches
    matches = re.findall(pattern, content)
    if not matches:
        print("No version parameters (?v=...) found in index.html.")
        return False
        
    # Replace all matches with new version
    updated_content = re.sub(pattern, rf"\g<1>{timestamp}", content)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print(f"Successfully bumped cache-busting version in index.html to {timestamp}.")
    return True

if __name__ == "__main__":
    bump_html_versions()
