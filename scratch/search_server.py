import sys

# Configure stdout/stderr to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("Starting curation server analysis...")
try:
    with open('curator_server.py', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    output_lines = []
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in ['spreadsheets', 'sheet_id', 'sheet', 'POOL', 'SOURCE', 'Source', 'Pool', 'tk-', 'duplicate']):
            output_lines.append(f"Line {i+1}: {line.strip()}")

    with open('scratch/output.txt', 'w', encoding='utf-8') as f_out:
        f_out.write('\n'.join(output_lines))
    print(f"Analysis completed successfully. Found {len(output_lines)} lines.")
except Exception as e:
    print("Error:", e)
