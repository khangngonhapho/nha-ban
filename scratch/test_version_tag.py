import requests

urls = [
    "https://res.cloudinary.com/deru9p712/image/upload/v1779916662/BDS-KhangNgo/csweaw-mjfmhkqd-8e55866b/xdwlvjirk0kyipnxviaa.jpg",
    "https://res.cloudinary.com/deru9p712/image/upload/BDS-KhangNgo/csweaw-mjfmhkqd-8e55866b/xdwlvjirk0kyipnxviaa.jpg",
    "https://res.cloudinary.com/deru9p712/image/upload/v1779875767/BDS-KhangNgo/6hianw-mnfnt9s4-5b9bc1cc/o811mvzyhrucicnwriyf.jpg",
    "https://res.cloudinary.com/deru9p712/image/upload/BDS-KhangNgo/6hianw-mnfnt9s4-5b9bc1cc/o811mvzyhrucicnwriyf.jpg"
]

for url in urls:
    r = requests.head(url)
    print(f"URL: {url}\nStatus: {r.status_code}\n")
