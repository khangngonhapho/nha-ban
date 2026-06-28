import os

assets_dir = "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\docs\\workflows\\assets"
if os.path.exists(assets_dir):
    print(f"Listing files in {assets_dir}:")
    for f in os.listdir(assets_dir):
        print(f)
else:
    print(f"Directory {assets_dir} does not exist!")
