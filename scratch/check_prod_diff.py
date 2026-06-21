# -*- coding: utf-8 -*-
import requests
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

local_helpers_path = "static/js/lego_helpers.js"
local_filters_path = "static/js/lego_filters.js"

r_helpers = requests.get('https://khangngonhapho.vercel.app/static/js/lego_helpers.js')
r_filters = requests.get('https://khangngonhapho.vercel.app/static/js/lego_filters.js')

print(f"Prod helpers length: {len(r_helpers.text)}")
print(f"Prod filters length: {len(r_filters.text)}")

if os.path.exists(local_helpers_path):
    with open(local_helpers_path, 'r', encoding='utf-8') as f:
        local_helpers = f.read()
    print(f"Local helpers length: {len(local_helpers)}")
    print(f"Helpers match: {r_helpers.text == local_helpers}")
    if r_helpers.text != local_helpers:
        print("Helpers differ! Showing first diff line...")
        # simple line diff
        p_lines = r_helpers.text.splitlines()
        l_lines = local_helpers.splitlines()
        for idx, (p_l, l_l) in enumerate(zip(p_lines, l_lines)):
            if p_l != l_l:
                print(f"Line {idx+1} differs:")
                print(f"  Prod:  {p_l}")
                print(f"  Local: {l_l}")
                break
                
if os.path.exists(local_filters_path):
    with open(local_filters_path, 'r', encoding='utf-8') as f:
        local_filters = f.read()
    print(f"Local filters length: {len(local_filters)}")
    print(f"Filters match: {r_filters.text == local_filters}")
    if r_filters.text != local_filters:
        print("Filters differ!")
