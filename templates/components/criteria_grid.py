# -*- coding: utf-8 -*-
"""
Criteria grid component for BDS KhangNgo offline viewer.
"""

def render_criteria_grid(listing):
    criteria_fields = {k: v for k, v in listing.items() if k.startswith("Criteria_") and v}
    if not criteria_fields:
        return ""
        
    html = '<div class="section-title">Tiêu chí phân loại (Criteria)</div><div class="grid-criteria">'
    for k, v in criteria_fields.items():
        friendly_name = k.replace("Criteria_", "").replace("_", " ")
        html += f"""
        <div class="criteria-card">
            <span class="criteria-label">{friendly_name}</span>
            <span class="criteria-value">{v}</span>
        </div>
        """
    html += "</div>"
    return html
