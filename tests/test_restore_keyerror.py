import os
import sys
import json
import sqlite3
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pool_lego import init_db, POOL_HEADERS
import restore_db_from_sheets

def test_restore_keyerror_reproduction(tmp_path, monkeypatch):
    # Setup temporary database files
    db_file = str(tmp_path / "master.db")
    
    # Initialize the master database structure
    init_db(db_file=db_file)
    
    # Insert a listing that has curated_config_json containing "image_url" but no "url" key
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    tk_id = "2271be35-1e28-4868-9020-d65f15a93898"
    bad_curated_json = json.dumps({
        "images": [
            {
                "image_url": "https://example.com/image1.jpg",
                "r2_url": "",
                "role": "diagram",
                "sequence_index": 100,
                "is_hidden": 0
            },
            {
                "image_url": "https://example.com/image2.jpg",
                "r2_url": "",
                "role": "facade",
                "sequence_index": 0,
                "is_hidden": 0
            }
        ],
        "Ma_Khang_Ngô__ID_": "MWOTIZAIDQT"
    })
    
    # Add minimal required fields to listings
    cursor.execute("""
        INSERT INTO listings (tk_id, status, curated_config_json)
        VALUES (?, ?, ?)
    """, (tk_id, "raw_text", bad_curated_json))
    conn.commit()
    conn.close()
    
    # Monkeypatch restore_db_from_sheets variables
    monkeypatch.setattr(restore_db_from_sheets, "DB_FILE", db_file)
    
    # Prepare mock data for Google Sheets
    mock_pool_row = [""] * len(POOL_HEADERS)
    mock_pool_row[POOL_HEADERS.index("Mã Hàng")] = tk_id
    mock_pool_row[POOL_HEADERS.index("Link Gốc")] = f"https://thienkhoi.com/nha/{tk_id}"
    mock_pool_row[POOL_HEADERS.index("Sơ đồ thửa đất 1")] = "https://example.com/sodo.jpg"
    
    # Needs at least 3 rows to bypass the check
    mock_pool_values = [POOL_HEADERS, mock_pool_row, [""] * len(POOL_HEADERS)]
    
    # Mock gspread/Sheets connection
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_sheet = MagicMock()
    mock_sheet.get_all_values.return_value = mock_pool_values
    mock_spreadsheet.worksheet.return_value = mock_sheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    
    # Mock auth and config calls
    with patch("restore_db_from_sheets.get_google_credentials", return_value=MagicMock()), \
         patch("restore_db_from_sheets.load_config", return_value={}), \
         patch("gspread.authorize", return_value=mock_client), \
         patch("restore_db_from_sheets.restore_links_and_blacklist") as mock_restore_lbl:
         
        # Run restore_database which should load the cache and hit the error
        restore_db_from_sheets.restore_database()
