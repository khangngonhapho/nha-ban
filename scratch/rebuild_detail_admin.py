import subprocess
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def get_head_index_html():
    """Retrieve unmodified index.html from git HEAD."""
    try:
        content = subprocess.check_output(
            ["git", "show", "HEAD:index.html"],
            cwd="d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
        ).decode("utf-8")
        return content
    except Exception as e:
        print(f"Error getting index.html from HEAD: {e}")
        sys.exit(1)

def extract_js_block(content, start_pos):
    """Find the JavaScript block starting at start_pos, matching braces correctly."""
    brace_start = content.find('{', start_pos)
    if brace_start == -1:
        return ""
    
    brace_count = 1
    i = brace_start + 1
    in_string = False
    string_char = None
    escape = False
    
    while i < len(content) and brace_count > 0:
        char = content[i]
        if escape:
            escape = False
            i += 1
            continue
        if char == '\\':
            escape = True
            i += 1
            continue
        if in_string:
            if char == string_char:
                in_string = False
            i += 1
            continue
        if char in ["'", '"', '`']:
            in_string = True
            string_char = char
            i += 1
            continue
        
        # Ignore comments to prevent false brace counts
        if char == '/' and i + 1 < len(content):
            if content[i+1] == '/':
                newline_pos = content.find('\n', i)
                if newline_pos != -1:
                    i = newline_pos
                else:
                    i = len(content)
                continue
            elif content[i+1] == '*':
                end_comment = content.find('*/', i)
                if end_comment != -1:
                    i = end_comment + 2
                else:
                    i = len(content)
                continue
                
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        
        i += 1
        
    return content[start_pos:i]

def main():
    original_html = get_head_index_html()
    lines = original_html.splitlines()
    print(f"Total lines in HEAD index.html: {len(lines)}")
    
    # Precise 1-indexed line ranges to extract from unmodified index.html
    ranges_to_extract = [
        ("isListingSodoUrl", 2805, 2834),
        ("renderImageEditorWidget", 2836, 3211),
        ("slideImageEditorCarousel", 3219, 3226),
        ("gotoImageEditorSlide", 3228, 3260),
        ("handleCarouselTouchStart", 3266, 3268),
        ("handleCarouselTouchMove", 3270, 3272),
        ("handleCarouselTouchEnd", 3274, 3277),
        ("handleCarouselSwipe", 3279, 3289),
        ("removeImageFromPublicLists", 3292, 3308),
        ("removeImageFromSodo", 3310, 3327),
        ("activeImageToggleFacade", 3330, 3357),
        ("activeImageToggleCover", 3359, 3408),
        ("activeImageToggleSodo", 3410, 3472),
        ("activeImageTogglePublic", 3474, 3545),
        ("activeImageMoveOrder", 3548, 3601),
        ("reRenderCurationEditorInPlace", 3607, 3626),
        ("refreshImageEditorUI", 3629, 3835),
        ("compressImageClientSide", 3850, 3898),
        ("uploadFileToR2", 3900, 3946),
        ("handleLocalImageUpload", 3948, 4068),
        ("uncheckAllCurationImages", 4070, 4100),
        ("openPoolS", 4102, 4209),
        ("onPoolSearchToolKeyup", 4219, 4280),
        ("pullListingFromPoolRow", 4282, 4289),
        ("executePullFromPool", 4291, 4581),
        ("toggleAdminAccordion", 4586, 4598),
        ("getPublicImagesFromForm", 4600, 4693),
        ("openZoomOverlay", 4698, 4782),
        ("checkMoTaCollapse", 4784, 4798),
        ("toggleMotaGocCollapse", 4800, 4814),
        ("saveSourceChanges", 4873, 5210),
        ("saveNewListingFromPool", 5212, 5564)
    ]
    
    # Extract functions
    js_functions_code = []
    for name, start, end in ranges_to_extract:
        func_lines = lines[start-1:end]
        func_code = "\n".join(func_lines)
        js_functions_code.append(f"\n  // === {name} ===\n")
        js_functions_code.append(func_code)
        print(f"✅ Extracted: {name} (lines {start} to {end}, {len(func_code)} chars)")

    # Extract HTML template inside openS (lines 1569 to 1852 - inner HTML content)
    html_template_lines = lines[1568:1852] 
    html_template = "\n".join(html_template_lines)
    
    # Replace the preview accordion in the template with client webview iframe
    acc_preview_pattern = r'(<!-- ACCORDION 3: PREVIEW KHÁCH HÀNG -->\s*<div class="accordion-item" id="accPreview">.*?<div class="accordion-content">)(.*?)(</div>\s*</div>)'
    def replace_preview(match):
        header = match.group(1)
        footer = match.group(3)
        dynamic_content = """
            ${(p.id && !p.isFromPoolOnly) ? `
              <div class="preview-webview-container" style="position: relative; width: 100%; height: 600px; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; overflow: hidden; background: #1c1c1e; box-shadow: 0 4px 15px rgba(0,0,0,0.25);">
                <iframe src="${window.location.origin}${window.location.pathname}?s=${p.system_id}&preview=true" style="width: 100%; height: 100%; border: none;"></iframe>
              </div>
            ` : `
              <div style="padding: 24px 12px; text-align: center; color: var(--red); font-weight: 700; background: rgba(231, 76, 60, 0.05); border-radius: 8px; border: 1px dashed var(--red); font-size: 13px;">
                ⚠️ BĐS chưa được xuất bản (lên sóng). Hãy xuất bản tin để xem Preview Khách hàng.
              </div>
            `}
        """
        return header + dynamic_content + footer
        
    modified_html_template = re.sub(acc_preview_pattern, replace_preview, html_template, flags=re.DOTALL)
    
    # Dynamically extract the full post-render initialization block (Occurrence 3 of the statement)
    search_str = 'if (isAdmin && (p.original_row_data || p.isFromPoolOnly))'
    pos = 0
    for _ in range(3):
        pos = original_html.find(search_str, pos)
        if pos == -1:
            print("Error: Could not find occurrence 3 of post-render block.")
            sys.exit(1)
        if _ < 2:
            pos += len(search_str)
            
    post_render_code = extract_js_block(original_html, pos)
    print(f"✅ Extracted post-render initialization code block (Length: {len(post_render_code)} chars)")
    
    # Patch post_render_code to keep accPreview always visible
    post_render_code = post_render_code.replace(
        "if (accPreview) accPreview.style.display = 'none';",
        "if (accPreview) accPreview.style.display = 'block';"
    )
    
    # Bypass CSS display: flex !important overrides for speed dial buttons
    post_render_code = post_render_code.replace(
        "savePoolBtn.style.display = 'flex';",
        "savePoolBtn.style.setProperty('display', 'flex', 'important');"
    )
    post_render_code = post_render_code.replace(
        "savePoolBtn.style.display = 'none';",
        "savePoolBtn.style.setProperty('display', 'none', 'important');"
    )
    post_render_code = post_render_code.replace(
        "saveSourceBtn.style.display = 'flex';",
        "saveSourceBtn.style.setProperty('display', 'flex', 'important');"
    )

    # Reassemble LegoDetailAdmin.render code
    render_function_code = f"""
  function render(p, sbody, autoExpandPreview = false) {{
    const targetMatTien = p.img_mat_tien || (p.pool_row_data ? p.pool_row_data[29] : '') || '';
    const normMatTien = window.normalizeImgUrl ? window.normalizeImgUrl(targetMatTien) : '';
    const isFacadeUrl = (url) => {{
      if (!url) return false;
      const norm = window.normalizeImgUrl ? window.normalizeImgUrl(url) : '';
      return norm !== '' && norm === normMatTien;
    }};

    const cleanRawNoiDungChinh = (text) => {{
      if (!text) return '';
      const keyword = 'nguồn';
      const idx = text.toLowerCase().indexOf(keyword);
      if (idx !== -1) {{
        return text.substring(0, idx).trim();
      }}
      return text.trim();
    }};
    const cleanedNoiDungChinh = cleanRawNoiDungChinh(p.raw_noi_dung_chinh);

    const extractSource = (text) => {{
      if (!text) return 'Đầu chủ';
      const lower = text.toLowerCase();
      if (lower.includes('nguồn đối tác') || lower.includes('nguon doi tac') || lower.includes('nguon i tc') || lower.includes('nguồn đt') || lower.includes('nguon dt')) {{
        return 'Đối tác';
      }}
      if (lower.includes('nguồn đầu chủ') || lower.includes('nguon dau chu') || lower.includes('nguon u ch')) {{
        return 'Đầu chủ';
      }}
      const match = text.match(/nguồn\\s+([a-zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ\\s]+)/i);
      if (match) return match[1].trim();
      const matchNguon = text.match(/nguon\\s+([A-Za-z\\s]+)/i);
      if (matchNguon) return matchNguon[1].trim();
      return 'Đầu chủ';
    }};

    const extractCommission = (p) => {{
      if (typeof window.extractCommission === 'function') {{
        return window.extractCommission(p);
      }}
      return '-';
    }};

    const formatRawDescription = (text) => {{
      if (typeof window.formatRawDescription === 'function') {{
        return window.formatRawDescription(text);
      }}
      return text || '';
    }};

    const renderImageEditorWidget = (p) => {{
      if (typeof window.renderImageEditorWidget === 'function') {{
        return window.renderImageEditorWidget(p);
      }}
      return '';
    }};

    // RENDER HTML TEMPLATE
    sbody.innerHTML = `{modified_html_template}`;

    // POST-RENDER INITIALIZATION
    {post_render_code}
  }}
"""

    # Package everything in IIFE
    js_content = f"""// Lego Frontend - Admin Curation & Detail View Module
// US-094F: Cô lập Module Chi tiết, Preview & Curation dành riêng cho Admin

(function() {{
  'use strict';

  // Export module LegoDetailAdmin
  window.LegoDetailAdmin = {{
    render: render
  }};

  {render_function_code}

  {"".join(js_functions_code)}

  // Register remaining aliases on window for backward compatibility
  window.compressImageClientSide = compressImageClientSide;
  window.uploadFileToR2 = uploadFileToR2;
  window.executePullFromPool = executePullFromPool;
  window.renderImageEditorWidget = renderImageEditorWidget;
  window.isListingSodoUrl = isListingSodoUrl;
  window.slideImageEditorCarousel = slideImageEditorCarousel;
  window.gotoImageEditorSlide = gotoImageEditorSlide;
  window.handleCarouselTouchStart = handleCarouselTouchStart;
  window.handleCarouselTouchMove = handleCarouselTouchMove;
  window.handleCarouselTouchEnd = handleCarouselTouchEnd;
  window.handleCarouselSwipe = handleCarouselSwipe;
  window.removeImageFromPublicLists = removeImageFromPublicLists;
  window.removeImageFromSodo = removeImageFromSodo;
  window.activeImageToggleFacade = activeImageToggleFacade;
  window.activeImageToggleCover = activeImageToggleCover;
  window.activeImageToggleSodo = activeImageToggleSodo;
  window.activeImageTogglePublic = activeImageTogglePublic;
  window.activeImageMoveOrder = activeImageMoveOrder;
  window.reRenderCurationEditorInPlace = reRenderCurationEditorInPlace;
  window.refreshImageEditorUI = refreshImageEditorUI;
  window.handleLocalImageUpload = handleLocalImageUpload;
  window.uncheckAllCurationImages = uncheckAllCurationImages;
  window.openPoolS = openPoolS;
  window.onPoolSearchToolKeyup = onPoolSearchToolKeyup;
  window.pullListingFromPoolRow = pullListingFromPoolRow;
  window.toggleAdminAccordion = toggleAdminAccordion;
  window.getPublicImagesFromForm = getPublicImagesFromForm;
  window.openZoomOverlay = openZoomOverlay;
  window.checkMoTaCollapse = checkMoTaCollapse;
  window.toggleMotaGocCollapse = toggleMotaGocCollapse;
  window.saveSourceChanges = saveSourceChanges;
  window.saveNewListingFromPool = saveNewListingFromPool;

  console.log("LegoDetailAdmin module initialized.");
}})();
"""

    # Write back to static/js/lego_detail_admin.js
    with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js", "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print("Successfully rebuilt static/js/lego_detail_admin.js with static line numbers and perfect brace matching!")

if __name__ == "__main__":
    main()
