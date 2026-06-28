import json

settings_path = "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\settings.json"
prompt_path = "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\system_prompt.txt"

# Read settings.json
with open(settings_path, "r", encoding="utf-8") as f:
    settings = json.load(f)

# Read prompt
with open(prompt_path, "r", encoding="utf-8") as f:
    prompt_content = f.read().strip()

settings["prompt_google_doc_id"] = "12LaUJ-34eolQ9ElgQhpe5k9Mh_bn4B7p31DQAZ1Ncto"
settings["openai_system_prompt"] = prompt_content

# Save settings.json
with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=4, ensure_ascii=False)

print("settings.json updated successfully!")
