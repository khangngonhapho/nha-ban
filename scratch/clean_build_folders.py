import os
import shutil
import stat

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

project_dir = "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo"

for folder in ["dist", "build"]:
    p = os.path.join(project_dir, folder)
    if os.path.exists(p):
        print(f"Cleaning {p}...")
        try:
            shutil.rmtree(p, onerror=remove_readonly)
            print(f"Cleaned {folder} successfully!")
        except Exception as e:
            print(f"Failed to clean {folder}: {e}")
    else:
        print(f"{folder} does not exist.")
