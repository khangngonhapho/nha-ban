# -*- coding: utf-8 -*-
import requests
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

sheet_id = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json"

response = requests.get(url)
print(f"Status code: {response.status_code}")
print(response.text[:500])
