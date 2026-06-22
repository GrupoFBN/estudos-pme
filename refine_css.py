import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ═══════════════════════════════════════════════════
# 1. Replace the minimal responsive section with a comprehensive mobile-first design
# ═══════════════════════════════════════════════════

old_responsive = """    /* ─── RESPONSIVE ─── */

    @media (max-width: 900px) {

      .page-wrap { grid-template-columns: 1fr; }

      .sidebar { position: static; flex-direction: row; flex-wrap: wrap; }

      .company-stats { display: none; }

    }

    @media (max-width: 600px) {

      .page-wrap { padding: 16px 12px; }

      header { padding: 0 16px; }

    }"""

new_responsive = """    /* ─── RESPONSIVE ─── */

    @media (max-width: 1100px) {
      .page-wrap { grid-template-columns: 220px 1fr; gap: 20px; }
      .company-header-content { flex-wrap: wrap; }
      .company-stats { margin-left: 0; margin-top: 8px; width: 100%; justify-content: flex-start; }
    }

    @media (max-width: 900px) {
      .page-wrap { grid-template-columns: 1fr; gap: 16px; padding: 20px 16px; }
      .sidebar {
        position: static; flex-direction: row; flex-wrap: nowrap;
        overflow-x: auto; gap: 8px; padding-bottom: 8px;
        max-height: none; -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
      }
      .sidebar::-webkit-scrollbar { display: none; }
      .sidebar-label { display: none; }
      .company-btn {
        flex-shrink: 0; white-space: nowrap;
        padding: 8px 14px; border-radius: 20px;
        border: 1px solid var(--border); background: var(--bg-card);
        gap: 8px; min-width: max-content;
      }
      .company-btn .cb-logo { width: 28px; height: 28px; border-radius: 6px; padding: 2px; }
      .company-btn .cb-icon { width: 28px; height: 28px; border-radius: 6px; font-size: 14px; }
      .company-btn .cb-name { font-size: 12px; }
      .company-count { font-size: 9px; padding: 1px 6px; }
      .company-btn.active {
        background: var(--accent); color: #fff; border-color: var(--accent);
      }
      .company-btn.active .cb-name { color: #fff; }
      .company-btn.active .company-count { background: rgba(255,255,255,0.2); color: #fff; }
      .company-btn.active .cb-logo { border-color: rgba(255,255,255,0.3); }
      .company-header-content { padding: 20px; gap: 16px; flex-wrap: wrap; }
      .company-logo-large { width: 56px; height: 56px; border-radius: 12px; padding: 6px; }
      .company-info h2 { font-size: 20px; }
      .company-stats { margin-left: 0; width: 100%; justify-content: space-between; margin-top: 4px; }
      .stat-box { padding: 10px 14px; min-width: 0; flex: 1; }
      .stat-box .sv { font-size: 16px; }
      .stat-box .sl { font-size: 8px; }
      .company-rede-btns { flex-wrap: wrap; }
      .summary-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
      .summary-card { padding: 14px; }
      .summary-card .total-value { font-size: 16px; }
      .section-header { padding: 16px; }
      .section-header h3 { font-size: 15px; }
      .compare-bar { padding: 12px 16px; flex-direction: column; gap: 10px; }
      .compare-bar-info { width: 100%; justify-content: center; }
    }

    @media (max-width: 500px) {
      .page-wrap { padding: 12px 8px; }
      header { padding: 0 12px; }
      .header-inner { height: 56px; gap: 10px; }
      .logo-badge { height: 36px; }
      .header-title h1 { font-size: 14px; }
      .header-title p { font-size: 10px; }
      .company-header-content { padding: 16px; gap: 12px; }
      .company-logo-large { width: 48px; height: 48px; border-radius: 10px; padding: 4px; }
      .company-info h2 { font-size: 18px; }
      .company-info p { font-size: 11px; gap: 4px; }
      .stat-box { padding: 8px 10px; border-radius: 10px; }
      .stat-box .sv { font-size: 14px; }
      .summary-grid { grid-template-columns: 1fr 1fr; gap: 8px; }
      .summary-card { padding: 12px; }
      .summary-card .plan-name { font-size: 11px; }
      .summary-card .total-value { font-size: 15px; }
      .btn-rede { font-size: 11px; padding: 5px 10px; }
      .section-card { margin-bottom: 16px; }
      .diferenciais-box { padding: 16px; }
      table { font-size: 11px; }
      td, th { padding: 8px 10px; }
    }"""

content = content.replace(old_responsive, new_responsive)

# ═══════════════════════════════════════════════════
# 2. Refine header - add subtle gradient bottom line
# ═══════════════════════════════════════════════════

old_header = """    header {

      background: #ffffff;

      border-bottom: 1px solid var(--border);

      padding: 0 32px;

      position: sticky;

      top: 0;

      z-index: 100;

      box-shadow: 0 4px 12px rgba(0,0,0,0.03);

    }"""

new_header = """    header {
      background: #ffffff;
      border-bottom: none;
      padding: 0 32px;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 1px 0 var(--border), 0 4px 20px rgba(48,86,156,0.06);
    }"""

content = content.replace(old_header, new_header)

# ═══════════════════════════════════════════════════
# 3. Refine sidebar gap and background
# ═══════════════════════════════════════════════════

old_sidebar = """    .sidebar {

      position: sticky;

      top: 80px;

      display: flex;

      flex-direction: column;

      gap: 10px;

      max-height: calc(100vh - 100px);

      overflow-y: auto;

      padding-right: 4px;

    }"""

new_sidebar = """    .sidebar {
      position: sticky;
      top: 80px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      max-height: calc(100vh - 100px);
      overflow-y: auto;
      padding: 12px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }"""

content = content.replace(old_sidebar, new_sidebar)

# ═══════════════════════════════════════════════════
# 4. Refine summary cards hover color to FBN blue
# ═══════════════════════════════════════════════════

content = content.replace(
    'border-color: rgba(79,142,247,0.3);\n\n      transform: translateY(-2px);\n\n      box-shadow: var(--shadow);',
    'border-color: rgba(48,86,156,0.3);\n      transform: translateY(-2px);\n      box-shadow: 0 8px 24px rgba(48,86,156,0.12);'
)

# ═══════════════════════════════════════════════════
# 5. Refine diferenciais box for a more premium look  
# ═══════════════════════════════════════════════════

old_dif = """    .diferenciais-box {

      margin-top: 24px; background: rgba(79, 142, 247, 0.05);

      border: 1px solid rgba(79, 142, 247, 0.2); border-radius: var(--radius);

      padding: 20px 24px;

    }"""

new_dif = """    .diferenciais-box {
      margin-top: 24px;
      background: linear-gradient(135deg, rgba(48,86,156,0.03) 0%, rgba(46,203,150,0.03) 100%);
      border: 1px solid rgba(48,86,156,0.12);
      border-radius: var(--radius);
      padding: 24px 28px;
      border-left: 4px solid var(--accent);
    }"""

content = content.replace(old_dif, new_dif)

# ═══════════════════════════════════════════════════
# 6. Improve section header icons with FBN blue tones
# ═══════════════════════════════════════════════════

content = content.replace(
    '.section-card.copar-parcial { border-top: 4px solid #f5a623; }',
    '.section-card.copar-parcial { border-top: 4px solid #e5a336; }'
)

# ═══════════════════════════════════════════════════
# 7. Refine scrollbar for the whole page  
# ═══════════════════════════════════════════════════

old_scrollbar = """    /* scrollbar */

    ::-webkit-scrollbar { width: 6px; height: 6px; }

    ::-webkit-scrollbar-track { background: transparent; }

    ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 3px; }

    ::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.2); }"""

new_scrollbar = """    /* scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(48,86,156,0.15); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(48,86,156,0.3); }

    /* Mobile bottom nav helper */
    .mobile-nav-hint {
      display: none;
      text-align: center;
      font-size: 10px;
      color: var(--text-dim);
      padding: 4px 0 8px;
      letter-spacing: 0.05em;
    }
    @media (max-width: 900px) {
      .mobile-nav-hint { display: block; }
    }"""

content = content.replace(old_scrollbar, new_scrollbar)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
