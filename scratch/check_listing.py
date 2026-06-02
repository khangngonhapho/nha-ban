import json
import os
import sys

def check():
    path = "sheet_data.json"
    print(f"Reading from: {path}")
    if not os.path.exists(path):
        print("No sheet_data.json file found!")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"File size: {len(content)} bytes")
    
    # Try parsing
    try:
        if "setResponse(" in content:
            start = content.find("setResponse(") + 12
            end = content.rfind(")")
            content_json = content[start:end]
            data = json.loads(content_json)
        else:
            data = json.loads(content)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return

    # Check structure
    if isinstance(data, dict) and "values" in data:
        rows = data["values"]
    elif isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and "table" in data:
        rows = []
        table = data["table"]
        for r in table.get("rows", []):
            cells = [c.get("v") if c else None for c in r.get("c", [])]
            rows.append(cells)
    else:
        print("Unknown JSON structure:", type(data))
        return

    print(f"Total rows found: {len(rows)}")
    
    out_lines = []
    out_lines.append(f"Total rows found: {len(rows)}")
    
    for idx, r in enumerate(rows):
        if not r:
            continue
        r_str = " ".join([str(x) for x in r if x is not None])
        if "Nguyễn Thiện Thuật" in r_str or "175.51" in r_str:
            out_lines.append(f"\n--- Row {idx+2} ---")
            out_lines.append(f"Row data length: {len(r)}")
            for c_idx, cell in enumerate(r):
                out_lines.append(f"  Col {c_idx}: {cell}")

    output_path = "scratch/listing_output.txt"
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(out_lines))
    print(f"Output successfully written to: {output_path}")

if __name__ == "__main__":
    check()
