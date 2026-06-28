import shutil
import os

source_dir = r"C:\Users\Khang Ngo\.gemini\antigravity\brain\595fc691-aac4-4d6b-9257-a1e94612755c"
target_dir = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\docs\workflows\assets"

files_to_copy = {
    "admin_curation_desktop.png": "US-105_desktop.png",
    "admin_curation_mobile.png": "US-105_mobile.png"
}

for src_name, tgt_name in files_to_copy.items():
    src_path = os.path.join(source_dir, src_name)
    tgt_path = os.path.join(target_dir, tgt_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, tgt_path)
        print(f"Copied {src_name} to {tgt_name} successfully!")
    else:
        print(f"Source file {src_path} does not exist!")
