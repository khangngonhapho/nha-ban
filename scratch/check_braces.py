with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Let's trace braces in the style section
# Let's find the <style> start and end
style_start = -1
style_end = -1
for idx, line in enumerate(lines):
    if '<style>' in line:
        style_start = idx
    if '</style>' in line:
        style_end = idx
        break

print(f"Style tag lines: {style_start + 1} to {style_end + 1}")

# Let's parse media queries and their braces
stack = []
active_media = None
out = []

# Regex for media query
import re
media_pat = re.compile(r'@media\s*([^{]+)\{')

for idx in range(style_start, style_end):
    line = lines[idx]
    
    # Check for media query definition
    media_match = media_pat.search(line)
    if media_match:
        active_media = media_match.group(1).strip()
        stack.append(('media', active_media, idx + 1))
        out.append(f"Line {idx+1}: OPEN media query: @media {active_media}")
        continue
        
    # Trace opening and closing braces
    for char_idx, char in enumerate(line):
        if char == '{':
            stack.append(('brace', idx + 1))
        elif char == '}':
            if stack:
                top = stack.pop()
                if top[0] == 'media':
                    out.append(f"Line {idx+1}: CLOSE media query: @media {top[1]}")
                    active_media = None
                elif top[0] == 'brace':
                    # Check if the parent in stack is a media query
                    if stack and stack[-1][0] == 'media':
                        # This brace is inside media, but let's see if the next is close media
                        pass
            else:
                out.append(f"Line {idx+1}: Extra closing brace found!")

# Let's check where "#filterPanel" is relative to media queries
out.append("\n--- #filterPanel declarations and active media query scope ---")
current_media = None
media_stack = []
for idx in range(style_start, style_end):
    line = lines[idx]
    media_match = media_pat.search(line)
    if media_match:
        current_media = media_match.group(1).strip()
        media_stack.append(current_media)
    
    # Check brace counts to see when media closes
    # (Simple line-based check: count '{' and '}')
    if '#filterPanel' in line:
        out.append(f"Line {idx+1}: Found '#filterPanel' | Active media context: {current_media}")
        
    for char in line:
        if char == '{':
            media_stack.append('{')
        elif char == '}':
            if media_stack:
                val = media_stack.pop()
                if val != '{':
                    # closed a media query
                    current_media = None

with open('scratch/brace_trace.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done tracing braces")
