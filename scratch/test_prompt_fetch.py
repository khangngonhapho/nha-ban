import sys
import os

# Configure sys.stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.append("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo")

try:
    import manager
    print("--- Testing clean_prompt_content ---")
    dirty_text = "Thẻ 1\nNgày 08.06.2026\n—--------------\nBạn hãy đóng vai là Đầu chủ Trà Mi - chuyên gia..."
    clean = manager.clean_prompt_content(dirty_text)
    print(f"Cleaned: {clean[:100]}...")
    
    print("\n--- Testing fetch_google_doc_content ---")
    doc_id = "12LaUJ-34eolQ9ElgQhpe5k9Mh_bn4B7p31DQAZ1Ncto"
    # Call fetch_google_doc_content
    result = manager.fetch_google_doc_content(doc_id)
    if result:
        print(f"Success! Fetched content length: {len(result)}")
        print("First 200 characters of fetched result:")
        print(result[:200])
    else:
        print("Failed to fetch Google Doc content!")

    print("\n--- Testing get_default_system_prompt ---")
    default_prompt = manager.get_default_system_prompt()
    print(f"Default prompt length: {len(default_prompt)}")
    print("First 200 characters of default prompt:")
    print(default_prompt[:200])

except Exception as e:
    import traceback
    traceback.print_exc()
