import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pool_lego import POOL_HEADERS

sys.stdout.reconfigure(encoding='utf-8')

print("POOL_HEADERS:")
for idx, h in enumerate(POOL_HEADERS):
    if 'huong' in h.lower() or 'hướng' in h.lower():
        print(f"Index {idx}: {repr(h)}")
