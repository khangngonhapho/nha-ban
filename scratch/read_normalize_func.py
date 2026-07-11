import sys
import os
import inspect

sys.path.append(os.getcwd())
import manager

# Print the source code of normalize_listing_for_client
try:
    source = inspect.getsource(manager.normalize_listing_for_client)
    print("normalize_listing_for_client source:")
    print(source)
except Exception as e:
    print("Error:", e)
