"""
Script to refine the design of the health insurance comparison tool
- More elegant, corporate feel
- Mobile optimized
"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes_made = 0

# ═══════════════════════════════════════════════════
# 1. Refine the summary cards - make them feel more premium
# ═══════════════════════════════════════════════════

# Better summary card styling
old = '    .summary-card {\n\n      background: var(--bg-card);\n\n      border: 1px solid var(--border);\n\n      border-radius: var(--radius);\n\n      padding: 16px;\n\n      transition: all var(--transition);\n\n      cursor: pointer;\n\n    }'
new = '''    .summary-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }
    .summary-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--accent), var(--accent3));
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    .summary-card:hover::before { opacity: 1; }'''

if old in content:
    content = content.replace(old, new)
    changes_made += 1
    print(f"Change {changes_made}: Refined summary cards")

# Better summary card hover
old2 = "      border-color: rgba(48,86,156,0.3);\n      transform: translateY(-2px);\n      box-shadow: 0 8px 24px rgba(48,86,156,0.12);"
new2 = "      border-color: rgba(48,86,156,0.35);\n      transform: translateY(-3px);\n      box-shadow: 0 12px 32px rgba(48,86,156,0.15);"

if old2 in content:
    content = content.replace(old2, new2)
    changes_made += 1
    print(f"Change {changes_made}: Refined summary card hover")

# ═══════════════════════════════════════════════════
# 2. Refine the section cards
# ═══════════════════════════════════════════════════

old3 = '''    .section-card {

      background: var(--bg-card);

      border: 1px solid var(--border);

      border-radius: var(--radius);

      overflow: hidden;

      margin-bottom: 24px;

    }'''
new3 = '''    .section-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      margin-bottom: 20px;
      box-shadow: 0 2px 12px rgba(48,86,156,0.04);
      transition: box-shadow 0.3s ease;
    }
    .section-card:hover {
      box-shadow: 0 4px 20px rgba(48,86,156,0.08);
    }'''

if old3 in content:
    content = content.replace(old3, new3)
    changes_made += 1
    print(f"Change {changes_made}: Refined section cards")

# ═══════════════════════════════════════════════════
# 3. Improve the table styling for better readability
# ═══════════════════════════════════════════════════

old4 = '''    table {

      width: 100%; border-collapse: collapse; font-size: 12.5px;

      white-space: nowrap;

    }'''
new4 = '''    table {
      width: 100%; border-collapse: collapse; font-size: 12.5px;
      white-space: nowrap;
    }
    @media (max-width: 900px) {
      table { font-size: 11px; }
    }
    @media (max-width: 500px) {
      table { font-size: 10px; }
    }'''

if old4 in content:
    content = content.replace(old4, new4)
    changes_made += 1
    print(f"Change {changes_made}: Improved table responsiveness")

# ═══════════════════════════════════════════════════
# 4. Better cell-best highlight for the lowest price
# ═══════════════════════════════════════════════════

# Find and improve cell-best styling
old5 = '''      color: var(--accent3); font-weight: 700;

    }'''
# Check if this pattern exists
if old5 in content:
    new5 = '''      color: var(--accent3); font-weight: 700;
      position: relative;
    }
    .cell-best::after {
      content: '';
      position: absolute;
      bottom: 0; left: 8px; right: 8px;
      height: 2px;
      background: var(--accent3);
      border-radius: 1px;
    }'''
    content = content.replace(old5, new5, 1)  # Only first occurrence
    changes_made += 1
    print(f"Change {changes_made}: Enhanced best price indicator")

# ═══════════════════════════════════════════════════
# 5. Comprehensive mobile improvements 
# ═══════════════════════════════════════════════════

# Add better mobile breakpoints if not already present
mobile_css = '''
    /* ─── ENHANCED MOBILE ─── */
    @media (max-width: 768px) {
      .company-header-content {
        padding: 16px !important;
        gap: 12px !important;
      }
      .company-logo-large {
        width: 52px !important;
        height: 52px !important;
      }
      .company-info h2 {
        font-size: 18px !important;
      }
      .company-info p {
        font-size: 11px !important;
      }
      .company-stats {
        margin-left: 0 !important;
        width: 100% !important;
        gap: 6px !important;
      }
      .stat-box {
        padding: 10px 8px !important;
        min-width: 0 !important;
        flex: 1 !important;
        border-radius: 10px !important;
      }
      .stat-box .sv {
        font-size: 14px !important;
      }
      .stat-box .sl {
        font-size: 7px !important;
        margin-top: 4px !important;
      }
      .summary-grid {
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
      }
      .summary-card {
        padding: 12px !important;
      }
      .summary-card .plan-name {
        font-size: 11px !important;
      }
      .summary-card .total-value {
        font-size: 15px !important;
      }
      .section-header {
        padding: 14px !important;
      }
      .diferenciais-box {
        padding: 14px !important;
      }
      .table-wrap {
        margin: 0 -8px;
        padding: 0 8px;
      }
      .compare-bar {
        padding: 10px 12px !important;
      }
      .btn-rede {
        font-size: 10px !important;
        padding: 4px 10px !important;
      }
      .compare-toggle-btn {
        font-size: 10px !important;
        padding: 6px !important;
      }
    }

    @media (max-width: 480px) {
      header {
        padding: 0 10px !important;
      }
      .header-inner {
        height: 52px !important;
        gap: 8px !important;
      }
      .logo-badge {
        height: 32px !important;
      }
      .header-title h1 {
        font-size: 13px !important;
      }
      .header-title p {
        font-size: 9px !important;
      }
      .page-wrap {
        padding: 10px 6px !important;
      }
      .company-header-content {
        padding: 12px !important;
      }
      .company-logo-large {
        width: 44px !important;
        height: 44px !important;
        border-radius: 10px !important;
      }
      .company-info h2 {
        font-size: 16px !important;
      }
      .stat-box .sv {
        font-size: 13px !important;
      }
      .summary-grid {
        grid-template-columns: 1fr !important;
      }
    }'''

# Insert before </style>
content = content.replace('  </style>', mobile_css + '\n  </style>')
changes_made += 1
print(f"Change {changes_made}: Added comprehensive mobile styles")

# ═══════════════════════════════════════════════════
# 6. Add smooth scroll behavior
# ═══════════════════════════════════════════════════

old_html = '    html {' if '    html {' in content else None
if old_html is None:
    # Add html smooth scroll
    old_star = '    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }'
    new_star = '    html { scroll-behavior: smooth; }\n' + old_star
    if old_star in content:
        content = content.replace(old_star, new_star)
        changes_made += 1
        print(f"Change {changes_made}: Added smooth scroll behavior")

# ═══════════════════════════════════════════════════
# 7. Refine the compare toggle button 
# ═══════════════════════════════════════════════════

old_compare_btn = '''    .compare-toggle-btn {

      margin-top: 14px; width: 100%; background: rgba(0,0,0,0.05); border: 1px solid var(--border);

      color: var(--text-muted); padding: 8px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; transition: var(--transition);

    }'''

new_compare_btn = '''    .compare-toggle-btn {
      margin-top: 12px; width: 100%;
      background: linear-gradient(135deg, rgba(48,86,156,0.04), rgba(48,86,156,0.08));
      border: 1px solid rgba(48,86,156,0.15);
      color: var(--text-muted); padding: 8px 12px;
      border-radius: 8px; font-size: 11px; font-weight: 600;
      cursor: pointer; transition: all 0.2s ease;
      display: flex; align-items: center; justify-content: center; gap: 6px;
    }
    .compare-toggle-btn:hover {
      background: linear-gradient(135deg, rgba(48,86,156,0.08), rgba(48,86,156,0.14));
      border-color: rgba(48,86,156,0.3);
      color: var(--accent);
      transform: translateY(-1px);
    }'''

if old_compare_btn in content:
    content = content.replace(old_compare_btn, new_compare_btn)
    changes_made += 1
    print(f"Change {changes_made}: Refined compare toggle button")

# ═══════════════════════════════════════════════════  
# 8. Better total row highlighting
# ═══════════════════════════════════════════════════

old_total = '''    .total-row td {

      font-weight: 700;

      background: rgba(0,0,0,0.02);

      font-size: 13px;

    }'''

new_total = '''    .total-row td {
      font-weight: 700;
      background: linear-gradient(135deg, rgba(48,86,156,0.03), rgba(48,86,156,0.06));
      font-size: 13px;
      border-top: 2px solid rgba(48,86,156,0.15);
    }'''

if old_total in content:
    content = content.replace(old_total, new_total)
    changes_made += 1
    print(f"Change {changes_made}: Better total row highlight")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone! Total changes: {changes_made}")
