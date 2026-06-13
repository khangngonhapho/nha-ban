import os
import sys
import requests

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

cookie = ""
if os.path.exists("thienkhoi_cookie.txt"):
    with open("thienkhoi_cookie.txt", "r", encoding="utf-8") as f:
        cookie = f.read().strip()
        
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie
}

url = "https://data.thienkhoi.com/Hang/Detail/e3gsy4-mhkfviud-5073d0a3"
print(f"Kiểm tra Cookie với url: {url}")
r = requests.get(url, headers=headers, timeout=15)
print("Status code:", r.status_code)
print("Final URL:", r.url)
print("History:", r.history)

if "security.html" in r.url or "Account/Login" in r.url:
    print("[❌] COOKIE ĐÃ HẾT HẠN HOẶC BỊ CHẶN!")
else:
    print("[✅] COOKIE VẪN DÙNG TỐT!")
