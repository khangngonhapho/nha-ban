import zipfile
import os

zip_path = r'C:\Users\Khang Ngo\Downloads\BDS-KhangNgo_2026-06-12_16_09.zip'
extract_path = r'D:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Temp\cloudinary_backup'

print(f"Extracting {zip_path} to {extract_path}...")
os.makedirs(extract_path, exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Count files
extracted_count = 0
for root, dirs, files in os.walk(extract_path):
    extracted_count += len(files)
    
print(f"Extraction complete! Total files extracted: {extracted_count}")
