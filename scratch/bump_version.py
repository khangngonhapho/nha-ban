import re
import os
from datetime import datetime

def bump_version():
    index_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")
    if not os.path.exists(index_path):
        print(f"Error: index.html not found at {index_path}")
        return False
        
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    now_str = datetime.now().strftime("%Y%m%d%H%M")
    
    # Replace ?v=12digits with ?v=now_str
    pattern = re.compile(r"\?v=\d{12}")
    new_content, count = re.subn(pattern, f"?v={now_str}", content)
    
    if count > 0:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully bumped {count} version occurrences to ?v={now_str}")
        return True
    else:
        print("No version parameters matching ?v=12digits found.")
        return False

if __name__ == "__main__":
    bump_version()
