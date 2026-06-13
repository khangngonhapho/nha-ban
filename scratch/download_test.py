import requests

url = "https://res.cloudinary.com/deru9p712/image/upload/v1779875767/BDS-KhangNgo/6hianw-mnfnt9s4-5b9bc1cc/o811mvzyhrucicnwriyf.jpg"

print("GET request:")
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print("Status:", r.status_code)
print("Response headers:", dict(r.headers))
if r.status_code == 200:
    print("Content size:", len(r.content))
else:
    print("Error content:", r.text[:200])

print("\nHEAD request:")
r_head = requests.head(url, headers={'User-Agent': 'Mozilla/5.0'})
print("Status:", r_head.status_code)
