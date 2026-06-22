import codecs
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

missing_css = """
    .compare-badge { background: var(--accent); color: white; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 14px; }
    .btn-compare-action { background: var(--accent); color: #fff; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
    .btn-compare-action:hover { background: #3b76e2; }
    .btn-compare-action.secondary { background: rgba(0,0,0,0.1); }
    .btn-compare-action.secondary:hover { background: rgba(0,0,0,0.15); }
    .compare-toggle-btn {
      margin-top: 14px; width: 100%; background: rgba(0,0,0,0.05); border: 1px solid var(--border);
      color: var(--text-muted); padding: 8px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; transition: var(--transition);
    }
    .compare-toggle-btn.active { background: rgba(46, 203, 150, 0.15); border-color: var(--accent3); color: var(--accent3); }
    .compare-toggle-btn:hover { border-color: var(--text-muted); color: var(--text-main); }
    #compare-view { display: none; padding-bottom: 100px; }
    .compare-table-wrap {
      width: 100%; overflow-x: auto; background: var(--bg-card); border-radius: var(--radius); border: 1px solid var(--border);
    }
    .compare-table {
      width: 100%; border-collapse: collapse; text-align: left; min-width: 100%;
    }
    .compare-table th, .compare-table td {
      padding: 16px; border-bottom: 1px solid rgba(0,0,0,0.05); border-right: 1px solid rgba(0,0,0,0.05);
      vertical-align: top; font-size: 13px; white-space: normal;
    }
    .compare-table th {
      background: var(--bg-card2); font-weight: 600; color: var(--text-main);
    }
    .compare-table th:first-child, .compare-table td:first-child {
      position: sticky; left: 0; background: var(--bg-card2); z-index: 10; font-weight: 600; color: var(--text-muted); min-width: 180px; width: 180px; border-right: 2px solid rgba(0,0,0,0.1);
    }
    .compare-table th:first-child { z-index: 20; }
"""

content = content.replace("    .compare-table tr:hover td { background: rgba(0,0,0,0.02); }", missing_css + "    .compare-table tr:hover td { background: rgba(0,0,0,0.02); }")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
