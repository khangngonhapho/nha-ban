# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import os

sys.path.insert(0, os.getcwd())
import fetcher

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    html_file = "Thien Khoi Group - Nguon Hang - Chi Tiet New.html"
    if not os.path.exists(html_file):
        print(f"File {html_file} not found!")
        return

    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    # We will test scrape_criteria_from_dom with no multiselect info
    res = fetcher.scrape_criteria_from_dom(soup, "")
    print("Parsed criteria from DOM:")
    for k, v in res.items():
        print(f"  {k}: {repr(v)}")

    # Let's test with mock multiselect info to check fallback logic
    res_fallback = fetcher.scrape_criteria_from_dom(soup, "Ngõ thông,Thang máy,Có sổ - đang thế chấp ngân hàng")
    print("\nParsed criteria with multiselect fallback:")
    for k, v in res_fallback.items():
        print(f"  {k}: {repr(v)}")

if __name__ == "__main__":
    main()
