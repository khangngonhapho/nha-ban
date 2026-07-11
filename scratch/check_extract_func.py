import sys
import os
import inspect

# Reconfigure stdout to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.getcwd())
import pool_lego

# Print extract_json_ui_data source code
try:
    source = inspect.getsource(pool_lego.extract_json_ui_data)
    print("extract_json_ui_data source:")
    print(source)
except Exception as e:
    print("Error:", e)
