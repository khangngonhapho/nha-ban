import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

folder_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"

if os.path.exists(folder_path):
    print(f"=== Folder contents: {folder_path} ===")
    files = os.listdir(folder_path)
    print(f"Total files: {len(files)}")
    
    # Group by extension
    exts = {}
    for f in files:
        _, ext = os.path.splitext(f)
        ext = ext.lower()
        exts[ext] = exts.get(ext, 0) + 1
        
    print(f"File counts by extension: {exts}")
    
    # List files that are NOT images (.jpeg, .jpg, .png, .svg)
    non_img_files = []
    for f in files:
        name, ext = os.path.splitext(f)
        ext = ext.lower()
        # Handle dual extensions or downloaded suffixes like .js.tải xuống
        if not any(term in ext for term in [".jpeg", ".jpg", ".png", ".svg", ".gif"]):
            non_img_files.append(f)
            
    print(f"\nNon-image files ({len(non_img_files)}):")
    for f in non_img_files:
        fpath = os.path.join(folder_path, f)
        size = os.path.getsize(fpath)
        print(f"  {f} ({size} bytes)")
        
        # If it's small or text, let's peek inside
        if size < 50000 and f.endswith((".js", ".txt", ".json", "tải xuống")):
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_in:
                    content = file_in.read()
                # Check for keywords
                for kw in ["chủ nhà", "chuNha", "phone", "sodo", "sổ đỏ", "pháp lý"]:
                    if kw in content:
                        print(f"    -> Contains keyword '{kw}'!")
            except Exception:
                pass
else:
    print("Folder does not exist")
