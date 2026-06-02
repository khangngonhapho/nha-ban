import sys
import sqlite3
import json

# Configure stdout to use utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Import functions from curator_server
sys.path.append('.')
import curator_server

def test_ai():
    print("Loading config...")
    cfg = curator_server.load_config()
    # Mask API key for display
    api_key = cfg.get("openai_api_key", "")
    masked_key = api_key[:10] + "..." + api_key[-5:] if api_key else "None"
    print(f"OpenAI API Base: {cfg.get('openai_api_base')}")
    print(f"OpenAI API Key: {masked_key}")

    print("\nFetching latest listing from raw_archive.db...")
    conn = sqlite3.connect("raw_archive.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    row = cursor.execute("SELECT * FROM listings ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        print("No listings found in database!")
        conn.close()
        return
        
    d = dict(row)
    # Parse JSON fields just like in curator_server.py
    d["raw_images_tk"] = json.loads(d["raw_images_tk_json"]) if d.get("raw_images_tk_json") else []
    d["raw_drive_images"] = json.loads(d["raw_drive_images_json"]) if d.get("raw_drive_images_json") else []
    d["curated_config"] = json.loads(d["curated_config_json"]) if d.get("curated_config_json") else None
    
    print(f"Listing ID: {d['tk_id']}")
    print(f"Address: {d.get('Ngo_So_nha')} {d.get('Duong')}, Phường {d.get('Phuong')}, Quận {d.get('Quan')}")
    print(f"Noi_dung_chinh: '{d.get('Noi_dung_chinh')}'")
    print(f"Mo_ta_chi_tiet length: {len(d.get('Mo_ta_chi_tiet')) if d.get('Mo_ta_chi_tiet') else 0}")
    
    print("\nRunning AI curation backend...")
    result = curator_server.generate_ai_curation_for_listing_backend(d, cfg)
    
    print("\nRESULT FROM BACKEND:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    conn.close()

if __name__ == "__main__":
    test_ai()
