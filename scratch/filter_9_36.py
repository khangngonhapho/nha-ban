import json

def filter_results():
    with open('scratch/db_search_results.txt', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = []
    for d in data:
        row_str = str(list(d.values())).lower()
        if '9.36' in row_str or '36a' in row_str or '9/36' in row_str:
            matches.append(d)
            
    with open('scratch/pham_van_hai_9_36.txt', 'w', encoding='utf-8') as out:
        json.dump(matches, out, indent=2, ensure_ascii=False)
        
    print(f"Filtered count: {len(matches)}")

if __name__ == "__main__":
    filter_results()
