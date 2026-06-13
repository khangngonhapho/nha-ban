import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

user_cookie = """TKG_deviceId=670630f0-0b93-41e1-bf24-0a94b040e6fd; DO-LB="Cg0xMC4xLjAuMzozMzMzELDuyQU="; TKG_accessToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1N2M2ZWVmYS0yMjgwLTRkNjctOGQ2MC0wZjgzODM0Yzk0OWMiLCJ1c2VybmFtZSI6IjA3OTA3ODAyNDczNiIsIm5hbWUiOiJOZ8O0IFRow6FpIEtoYW5nIiwicHJvcGVydHlfcG9zdGluZ19saW1pdCI6NzUsInRva2VuVHlwZSI6IkFjY2Vzc1Rva2VuIiwiYXBwTG9naW4iOiJuZ3VvbmhhbmciLCJwbGF0Zm9ybSI6IndlYiIsImlhdCI6MTc4MDQ4OTg4OCwiZXhwIjoxNzgwNDkwNDg4fQ.R1NDhgsNTgh00fiPe462jXC0WrA2dL-6fcMqOOutu_Q; TKG_refreshToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1N2M2ZWVmYS0yMjgwLTRkNjctOGQ2MC0wZjgzODM0Yzk0OWMiLCJ1c2VybmFtZSI6IjA3OTA3ODAyNDczNiIsInRva2VuVHlwZSI6IlJlZnJlc2hUb2tlbiIsImFwcExvZ2luIjoibmd1b25oYW5nIiwicGxhdGZvcm0iOiJ3ZWIiLCJpYXQiOjE3ODA0ODk4ODgsImV4cCI6MTc4MDUzMzA4OH0.6jUVFR11n1fHigKs8gwz-24wyab-iC21nqqYmz8tysU;"""

file_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"

with open(file_path, "r", encoding="utf-8") as f:
    file_cookie = f.read().strip()

print("User cookie length:", len(user_cookie))
print("File cookie length:", len(file_cookie))

if user_cookie.strip() == file_cookie.strip():
    print("[✅] User cookie is IDENTICAL to thienkhoi_cookie.txt")
else:
    print("[❌] User cookie is DIFFERENT from thienkhoi_cookie.txt")
    # Show diff
    import difflib
    diff = list(difflib.ndiff(file_cookie.splitlines(), user_cookie.splitlines()))
    print("\n".join(diff))
