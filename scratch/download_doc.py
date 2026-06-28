import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc_id = "12LaUJ-34eolQ9ElgQhpe5k9Mh_bn4B7p31DQAZ1Ncto"
url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"

try:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
    print("Download successful!")
    print(f"Length of content: {len(content)}")
    print("First 200 characters:")
    print(content[:200])
    
    # Save it to system_prompt.txt
    with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\system_prompt.txt", "w", encoding="utf-8") as f:
        f.write(content.strip())
    print("Saved to system_prompt.txt!")
except Exception as e:
    print(f"Download failed: {e}")
