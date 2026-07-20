import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manager
from restore_db_from_sheets import merge_temp_to_master

def test_normalize_listing_for_client_overrides_phuong_quan():
    # Giả lập bản ghi từ SQLite
    row = {
        "tk_id": "test_tk_id",
        "Phuong": "Phuong Goc",
        "Quan": "Quan Goc",
        "custom_phuong": "Phuong Custom",
        "custom_quan": "Quan Custom",
        "custom_huong": "",
        "custom_dt_thuc_te": "",
        "custom_dt_so": ""
    }
    
    # normalized
    res = manager.normalize_listing_for_client(row)
    
    # Kiểm tra đã override thành công
    assert res["Phuong"] == "Phuong Custom"
    assert res["Quan"] == "Quan Custom"

def test_normalize_listing_for_client_fallback_when_empty():
    row = {
        "tk_id": "test_tk_id",
        "Phuong": "Phuong Goc",
        "Quan": "Quan Goc",
        "custom_phuong": "",
        "custom_quan": "",
        "custom_huong": "",
        "custom_dt_thuc_te": "",
        "custom_dt_so": ""
    }
    
    res = manager.normalize_listing_for_client(row)
    
    assert res["Phuong"] == "Phuong Goc"
    assert res["Quan"] == "Quan Goc"
