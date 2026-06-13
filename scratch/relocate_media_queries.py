import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's extract the style block
style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
if not style_match:
    print("Could not find style block")
    sys.exit(1)

style_content = style_match.group(1)
lines = style_content.split('\n')

# Find where media queries start and end in the style block lines
# The media queries are:
# 1) /* Responsive cho máy tính */ @media (min-width: 768px) { ... }
# 2) /* US-074: Modal width expansion on large screens */ @media (min-width: 1200px) { ... }
# Let's search for these lines
mq_start_idx = None
mq_end_idx = None

for i, line in enumerate(lines):
    if 'Responsive cho máy tính' in line or '@media (min-width: 768px)' in line:
        if mq_start_idx is None:
            mq_start_idx = i
            # Check a few lines back to see if we should include "Responsive cho máy tính" comment
            if i > 0 and 'Responsive cho máy tính' in lines[i-1]:
                mq_start_idx = i - 1

# Let's find the closing brace of @media (min-width: 1200px) or after the end of 768px + 1200px
# The 1200px query ends with:
#     @media (min-width: 1200px) {
#       .sheet {
#         width: 1100px !important;
#       }
#     }
# Let's find this pattern
for i in range(len(lines) - 1, -1, -1):
    if 'width: 1100px !important;' in lines[i]:
        # The closing brace of 1200px is 2 lines below this
        mq_end_idx = i + 2
        break

if mq_start_idx is None or mq_end_idx is None:
    print(f"Could not find media query indices. start: {mq_start_idx}, end: {mq_end_idx}")
    sys.exit(1)

print(f"Relocating style lines {mq_start_idx+1} to {mq_end_idx+1}")
mq_block = '\n'.join(lines[mq_start_idx:mq_end_idx])

# Let's update the filter panel selectors inside mq_block to use #filterPanel.open instead of #filterPanel
print("Updating #filterPanel selectors to #filterPanel.open inside media query...")
# We replace '#filterPanel' with '#filterPanel.open' but not '#filterPanel.open' already
# Since we might have already used #filterPanel.open, let's replace '#filterPanel' with '#filterPanel.open' and normalize
mq_block = mq_block.replace('#filterPanel.open', '#filterPanel') # temporary normalize
mq_block = mq_block.replace('#filterPanel', '#filterPanel.open')

# Remove the media query block from its original position
new_style_lines = lines[:mq_start_idx] + lines[mq_end_idx:]

# Append the media query block at the very end of the stylesheet
new_style_lines.append('\n' + mq_block + '\n')

new_style_content = '\n'.join(new_style_lines)

# Replace the style content in the HTML
new_html = html.replace(style_content, new_style_content)

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Relocation completed successfully!")
