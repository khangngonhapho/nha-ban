import os
import re
import sys

# Add parent directory to sys.path to find local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_userscript_file_exists():
    path = os.path.join("static", "js", "thienkhoi_list_scraper.user.js")
    assert os.path.exists(path), f"Userscript file not found at {path}"
    print("[PASS] Userscript file exists.")

def test_userscript_headers():
    path = os.path.join("static", "js", "thienkhoi_list_scraper.user.js")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "==UserScript==" in content, "Missing ==UserScript== header"
    assert "==/UserScript==" in content, "Missing ==/UserScript== header"
    
    # Check key metadata fields
    assert "@match" in content, "Missing @match patterns"
    assert "GM_xmlhttpRequest" in content, "Missing GM_xmlhttpRequest grant"
    assert "localhost" in content, "Missing connect to localhost"
    print("[PASS] Userscript metadata headers are correct.")

def test_curator_dashboard_link():
    path = "curator.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that it contains link to static userscript
    assert "static/js/thienkhoi_list_scraper.user.js" in content, "Link to userscript missing in curator.html"
    assert "Tampermonkey Scraper" in content, "Scraper card title missing in curator.html"
    print("[PASS] Curator Dashboard contains correct link and card.")

def test_curator_data_compiled():
    # Make sure curator_html_data.py has the same content updated
    import curator_html_data
    content = curator_html_data.CURATOR_HTML_CONTENT
    assert "static/js/thienkhoi_list_scraper.user.js" in content, "Link missing in curator_html_data.py"
    assert "Tampermonkey Scraper" in content, "Scraper card title missing in curator_html_data.py"
    print("[PASS] curator_html_data.py is synchronized and compiled.")

if __name__ == "__main__":
    print("==================================================")
    print("        RUNNING USERSCRIPT INTEGRATION TESTS       ")
    print("==================================================")
    try:
        test_userscript_file_exists()
        test_userscript_headers()
        test_curator_dashboard_link()
        test_curator_data_compiled()
        print("==================================================")
        print(" [SUCCESS] All Userscript integration tests passed!")
        print("==================================================")
    except AssertionError as e:
        print(f"[FAIL] Integration test failed: {e}")
        exit(1)
