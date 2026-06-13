# Simulate JS uploader and rendering logic
# We want to see if rendering the widget fails or omits the new image URL

# Mock normalizeImgUrl
def normalize_img_url(url):
    if not url:
        return ''
    clean = url.strip()
    # Mock drive/cloudinary match
    return clean

def render_image_editor_widget(p):
    cards = []
    
    # 1. Sodo 1-5
    sodo1Url = p['pool_row_data'][27] if p.get('pool_row_data') else p.get('raw_sodo1', '')
    if sodo1Url: cards.append({'type': 'sodo', 'index': 1, 'url': sodo1Url})
    sodo2Url = p['pool_row_data'][28] if p.get('pool_row_data') else p.get('raw_sodo2', '')
    if sodo2Url: cards.append({'type': 'sodo', 'index': 2, 'url': sodo2Url})
    sodo3Url = p['pool_row_data'][80] if p.get('pool_row_data') else p.get('raw_sodo3', '')
    if sodo3Url: cards.append({'type': 'sodo', 'index': 3, 'url': sodo3Url})
    sodo4Url = p['pool_row_data'][81] if p.get('pool_row_data') else p.get('raw_sodo4', '')
    if sodo4Url: cards.append({'type': 'sodo', 'index': 4, 'url': sodo4Url})
    sodo5Url = p['pool_row_data'][82] if p.get('pool_row_data') else p.get('raw_sodo5', '')
    if sodo5Url: cards.append({'type': 'sodo', 'index': 5, 'url': sodo5Url})
    
    # 2. Facade
    facadeUrl = p['pool_row_data'][29] if p.get('pool_row_data') else p.get('img_mat_tien', '')
    if facadeUrl: cards.append({'type': 'facade', 'index': 0, 'url': facadeUrl})
    
    # 3. Interior 1-25
    for i in range(1, 26):
        idx = (39 + i) if i <= 15 else (67 + i)
        url = p['pool_row_data'][idx] if p.get('pool_row_data') else (p.get('imgs')[i-1] if p.get('imgs') and len(p['imgs']) > i-1 else '')
        if url:
            cards.append({'type': 'interior', 'index': i, 'url': url})
            
    # 4. Alley 1-10
    for i in range(1, 11):
        url = p['pool_row_data'][29 + i] if p.get('pool_row_data') else ''
        if url:
            cards.append({'type': 'alley', 'index': i, 'url': url})
            
    # Deduplication and shouldRender logic
    is_sodo_url = lambda u: u in [sodo1Url, sodo2Url, sodo3Url, sodo4Url, sodo5Url]
    
    priority_list = []
    # interior > 1 or alley
    priority_list.extend([c for c in cards if (c['type'] == 'interior' and c['index'] > 1) or c['type'] == 'alley'])
    # interior == 1 or sodo or facade
    priority_list.extend([c for c in cards if (c['type'] == 'interior' and c['index'] == 1) or c['type'] == 'sodo' or c['type'] == 'facade'])
    
    rendered_urls = set()
    for c in priority_list:
        norm = normalize_img_url(c['url'])
        if not norm:
            c['should_render'] = False
            continue
        if (c['type'] == 'interior' or c['type'] == 'alley') and is_sodo_url(c['url']):
            c['should_render'] = False
            continue
        if norm not in rendered_urls:
            c['should_render'] = True
            rendered_urls.add(norm)
        else:
            c['should_render'] = False
            
    rendered_cards = [c for c in cards if c.get('should_render')]
    return cards, rendered_cards

def simulate():
    # Construct a mock listing p matched from Pool
    pool_row = [""] * 93
    pool_row[27] = "sodo1_url"
    # Fill interior 1 to 10
    for i in range(1, 11):
        pool_row[39 + i] = f"img_url_{i}"
        
    p = {
        'id': 'HWZOICBIMSIPDP',
        'imgs': [f"img_url_{i}" for i in range(1, 11)],
        'pool_row_data': pool_row,
        'isFromPoolOnly': False
    }
    
    print("BEFORE UPLOAD:")
    cards, rendered = render_image_editor_widget(p)
    print(f"Total cards: {len(cards)}, Rendered: {len(rendered)}")
    
    # Simulate uploading an interior image
    uploaded_url = "cloudinary_uploaded_new_interior_url"
    
    # handleLocalImageUpload interior logic
    assigned_idx = -1
    if p.get('pool_row_data'):
        # Pad
        row = p['pool_row_data']
        while len(row) < 90:
            row.append("")
        for j in range(1, 26):
            col_idx = (39 + j) if j <= 15 else (67 + j)
            if not row[col_idx]:
                row[col_idx] = uploaded_url
                assigned_idx = j
                break
                
    print(f"\nUploaded new image: assignedIdx = {assigned_idx}")
    print(f"Row colIdx {39 + assigned_idx} updated to: {p['pool_row_data'][39 + assigned_idx]}")
    
    print("\nAFTER UPLOAD:")
    cards_after, rendered_after = render_image_editor_widget(p)
    print(f"Total cards: {len(cards_after)}, Rendered: {len(rendered_after)}")
    
    # Check if new image is in cards and rendered
    in_cards = any(c['url'] == uploaded_url for c in cards_after)
    in_rendered = any(c['url'] == uploaded_url for c in rendered_after)
    print(f"Is new image in cards? {in_cards}")
    print(f"Is new image in rendered? {in_rendered}")
    for c in rendered_after:
        if c['url'] == uploaded_url:
            print("Found card:", c)

simulate()
