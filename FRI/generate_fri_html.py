"""
Generate FRI HTML presentation
Combines:
  - Plan pricing from Excel (by insurer)
  - RLA data: current plan per employee, invoice totals (scenario atual Porto Saude)
Same visual style as the Grupo Salus presentation.
"""
import json
import os
import re

# Load extracted data
base_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_dir, 'fri_data.json'), encoding='utf-8') as f:
    data = json.load(f)

# ── Data references ──
rla_emp = data['rla_empresa']
rla_sub = data['rla_subestipulante']
rla_subs = data.get('rla_subs', [])  # New: list of all subs including Aura
rla_aura = rla_subs[2]['data'] if len(rla_subs) > 2 else {'titulares': 0, 'dependentes': 0, 'total_vidas': 0, 'invoice_total': 0, 'premio_real': 0, 'iof': 0, 'persons': [], 'competencia': '', 'subestipulante': ''}
plans_excel = data['plans_excel']
empresa_name = data['empresa_name']
competencia = data['competencia']
fatura_total = data['fatura_total_atual']
total_vidas = data['total_vidas_atual']

# ── Helpers ──
def fmt_brl(v):
    if v is None:
        return '—'
    return f"R$\xa0{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_brl_compact(v):
    if v is None:
        return '—'
    s = f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"R$\xa0{s}"

def insurer_slug(name):
    name = name.lower().strip()
    if 'amil' in name and 'black' in name:
        return 'amil-black'
    if 'amil' in name and 'sele' in name:
        return 'amil-sel'
    if 'amil' in name and 'linha' in name:
        return 'amil-linha'
    if 'amil' in name:
        return 'amil'
    if 'bradesco' in name:
        return 'bradesco'
    if 'sulam' in name or 'sul am' in name:
        return 'sulamerica'
    if 'hapvida' in name and 'smart' in name:
        return 'hapvida-smart'
    if 'hapvida' in name:
        return 'hapvida'
    if 'unimed' in name:
        return 'unimed'
    return re.sub(r'[^a-z0-9]', '-', name)

def insurer_color(name):
    n = name.lower()
    if 'amil' in n: return '#e63946'
    if 'bradesco' in n: return '#c0392b'
    if 'sulam' in n: return '#2980b9'
    if 'hapvida' in n: return '#16a085'
    if 'unimed' in n: return '#27ae60'
    return '#30569c'

def insurer_emoji(name):
    n = name.lower()
    if 'amil' in n: return '🏥'
    if 'bradesco' in n: return '🏛️'
    if 'sulam' in n: return '💙'
    if 'hapvida' in n: return '🌿'
    if 'unimed' in n: return '💚'
    return '🏢'

def get_logo_path(name):
    n = name.lower()
    if 'amil' in n:
        return '../assets/logos/logo-amil.png'
    if 'bradesco' in n:
        return '../assets/logos/bradesco-logo.png'
    if 'sul' in n or 'sulam' in n:
        return '../assets/logos/logo-sulamerica.png'
    if 'hap' in n or 'vida' in n:
        return '../assets/logos/logo-hapvida.png'
    if 'unimed' in n:
        return '../assets/logos/logo-unimed.png'
    if 'porto' in n:
        return '../assets/logos/logo-porto-saude.png'
    return None

# ── Plan Name Normalization ──
def normalize_plan_name(name):
    """Remove trailing dot (duplicate marker) from plan names."""
    name = name.strip()
    if name.endswith('.'):
        return name[:-1].strip() + ' (Apt)'
    return name

# ── Build employees summary by plan ──
# Combine all RLAs (FRI + KCB + Aura)
all_persons = []
for p in rla_emp.get('persons', []):
    p['unidade'] = rla_emp.get('subestipulante', 'FRI Principal')
    all_persons.append(p)
for p in rla_sub.get('persons', []):
    p['unidade'] = rla_sub.get('subestipulante', 'KCB')
    all_persons.append(p)
for p in rla_aura.get('persons', []):
    p['unidade'] = 'AURA COSMETICOS E PERFUMARIA'
    all_persons.append(p)

# Group by plan
plan_groups = {}
for p in all_persons:
    plano = p.get('plano', '') or 'Não identificado'
    if plano not in plan_groups:
        plan_groups[plano] = []
    plan_groups[plano].append(p)

# Sort persons by value desc
for plano in plan_groups:
    plan_groups[plano].sort(key=lambda x: x.get('valor') or 0, reverse=True)

# ── Generate employees table rows ──
def gen_employees_table(persons, show_unidade=False):
    rows = []
    for p in persons:
        name = p.get('name', '').title()
        titularidade = p.get('titularidade', '')
        plano = p.get('plano', '') or '—'
        valor = p.get('valor')
        unidade = p.get('unidade', '')
        inicio = p.get('inicio_vigencia', '')
        
        badge_class = 'badge-titular' if titularidade == 'Titular' else 'badge-dep'
        badge_label = 'T' if titularidade == 'Titular' else 'D'
        valor_str = fmt_brl_compact(valor) if valor else '—'
        
        unidade_col = f'<td class="td-unidade">{unidade}</td>' if show_unidade else ''
        rows.append(f'''<tr>
          <td class="td-name"><span class="person-badge {badge_class}">{badge_label}</span> {name}</td>
          {unidade_col}
          <td class="td-plan">{plano}</td>
          <td class="td-inicio">{inicio}</td>
          <td class="td-valor">{valor_str}</td>
        </tr>''')
    return '\n'.join(rows)

# ── Lives distribution by age band (from Excel formulas) ──
def get_lives_for_band(label):
    lbl = str(label).strip().lower().replace('\xa0', ' ')
    if '0 a 18' in lbl: return 24   # Era 23 (+1: Ana Victoria, 13)
    if '19 a 23' in lbl: return 3   # Era 2  (+1: Monaliza, 21)
    if '24 a 28' in lbl: return 16
    if '29 a 33' in lbl: return 17
    if '34 a 38' in lbl: return 11  # Era 10 (+1: Rodrigo, 38)
    if '39 a 43' in lbl: return 8   # Era 7  (+1: Paulo, 43)
    if '44 a 48' in lbl: return 5
    if '49 a 53' in lbl: return 4   # Era 3  (+1: Ana Paula, 49)
    if '54 a 58' in lbl: return 2
    if '59 ou mais' in lbl: return 0
    return 0

# ── Recalculate Plan Totals based on new lives distribution ──
for ins in plans_excel:
    if not ins.get('plans') or not ins.get('age_data'):
        continue
    num_plans = len(ins['plans'])
    new_totals = [0.0] * num_plans
    for row in ins['age_data']:
        vidas = get_lives_for_band(row['label'])
        for i, val in enumerate(row['values']):
            if i < num_plans and isinstance(val, (int, float)):
                new_totals[i] += vidas * val
    ins['total'] = new_totals

# ── Link to network PDFs ──
def get_rede_buttons(name):
    n = name.lower()
    buttons = []
    if 'amil' in n and 'bronze' in n:
        buttons.append({'label': 'Rede Credenciada Hospitais', 'file': '../Rede/Amil bronze.pdf'})
        buttons.append({'label': 'Rede Credenciada Laboratórios', 'file': '../Rede/amil lab linha bronze.pdf'})
    elif 'amil' in n and 'sele' in n:
        buttons.append({'label': 'Rede Credenciada Hospitais', 'file': '../Rede/amil selecionada.pdf'})
    elif 'bradesco' in n:
        buttons.append({'label': 'Rede Credenciada Hospitais', 'file': '../Rede/rede crenciada bradesco hopsitais.pdf'})
        buttons.append({'label': 'Rede Credenciada Laboratórios', 'file': '../Rede/rede crenciada bradesco laboratórios.pdf'})
    elif 'sulam' in n:
        buttons.append({'label': 'Rede Credenciada', 'file': '../Rede/sulamerica.pdf'})
    
    if not buttons:
        return ''
    
    html = '<div class="company-rede-btns" style="margin-top: 10px; display: flex; gap: 8px;">'
    for btn in buttons:
        html += f'<a class="btn-rede" href="{btn["file"]}" target="_blank">📋 {btn["label"]}</a>'
    html += '</div>'
    return html

# ── Generate general notes card ──
def gen_notes_card(ins):
    notes = ins.get('notes', [])
    if not notes:
        return ''
    
    # Filter notes to remove any duplicates or empty items
    unique_notes = []
    for n in notes:
        n_clean = n.strip()
        # Remove asterisk strings like '***' or '*'
        n_clean_no_ast = n_clean.replace('*', '').strip()
        if n_clean_no_ast and n_clean not in unique_notes:
            unique_notes.append(n_clean)
            
    if not unique_notes:
        return ''
        
    li_items = ''.join(f'<li>{n}</li>' for n in unique_notes)
    
    return f'''
    <div class="diferenciais-box" style="margin-top: 24px;">
      <div class="diferenciais-title">
        <span style="font-size:16px">ℹ️</span> Regras de Aceitação & Informações Gerais
      </div>
      <ul class="diferenciais-list">
        {li_items}
      </ul>
    </div>
    '''

# ── Generate plan summary cards inside insurer panel ──
def gen_insurer_summary_cards(ins):
    name = ins['name']
    plans = ins['plans']
    age_data = ins['age_data']
    total = ins.get('total') or []
    
    valid_totals = [t for t in total if isinstance(t, (int, float))]
    min_total = min(valid_totals) if valid_totals else None
    
    cards = []
    for i, plan in enumerate(plans):
        pname = normalize_plan_name(plan)
        is_apt = '(Apt)' in pname
        v = total[i] if i < len(total) else None
        v_str = fmt_brl_compact(v) if v else '—'
        is_min = (min_total is not None and v == min_total)
        
        # Acomodacao from plans extra_features if available
        acom = 'Enfermaria'
        for f in ins.get('extra_features', []):
            if 'acomoda' in f['label'].lower():
                acom = f['values'][i] if i < len(f['values']) else 'Enfermaria'
                break
        
        is_apt_acom = 'apt' in acom.lower() or 'apart' in acom.lower()
        tag_class = 'tag-apt' if is_apt_acom else 'tag-enf'
        tag_text = 'APARTAMENTO' if is_apt_acom else 'ENFERMARIA'
        
        best_badge_html = '<div class="best-badge">★ Menor Preço</div>' if is_min else ''
        best_card_class = 'best-value' if is_min else ''
        
        cards.append(f'''
        <div class="summary-card {best_card_class}" data-plan-idx="{i}" data-acomodacao="{tag_text.lower()}" data-plan-total="{v or 0}" data-plan-name="{pname}" onclick="selectPlanCard('{insurer_slug(name)}', this)">
          {best_badge_html}
          <div class="plan-name" title="{pname}">{pname}</div>
          <div class="acomodacao-tag">
            <span class="{tag_class}">{tag_text}</span>
          </div>
          <div class="total-value">{v_str}</div>
          <div class="total-label">total {total_vidas} vidas/mês</div>
        </div>''')
    return '\n'.join(cards)

# ── Generate age table for an insurer ──
def gen_age_table(ins):
    plans = ins['plans']
    age_data = ins['age_data']
    total = ins.get('total')
    extra_features = ins.get('extra_features', [])
    
    if not plans or not age_data:
        return '<p class="empty-msg">Sem dados de tabela.</p>'
    
    # Find min value in each column for highlighting (excluding total, just age bands)
    col_mins = []
    for col_idx in range(len(plans)):
        vals = [row['values'][col_idx] for row in age_data if col_idx < len(row['values'])]
        col_mins.append(min(vals) if vals else None)
    
    # Header
    th_plans = ''
    for pi, pn in enumerate(plans):
        pname = normalize_plan_name(pn)
        is_apt = '(Apt)' in pname or 'apart' in pname.lower()
        th_class = 'th-apt' if is_apt else 'th-plan'
        th_plans += f'<th class="{th_class}">{pname}</th>'
    
    # Body rows (age bands)
    tbody = ''
    for row in age_data:
        num_vidas = get_lives_for_band(row['label'])
        tds = ''
        for ci, v in enumerate(row['values']):
            is_min = (col_mins[ci] is not None and v == col_mins[ci])
            cls = 'cell-best' if is_min else 'cell-value'
            tds += f'<td class="{cls}">{fmt_brl_compact(v)}</td>'
        tbody += f'<tr class="age-row"><td><strong>{row["label"]}</strong></td><td class="cell-vidas">{num_vidas}</td>{tds}</tr>'
    
    # Total row
    total_html = ''
    if total:
        total_tds = ''.join(f'<td>{fmt_brl_compact(v)}</td>' for v in total)
        total_html = f'<tr class="total-row"><td><strong>Total</strong></td><td class="cell-vidas">{total_vidas}</td>{total_tds}</tr>'
    
    # Extra features rows
    features_html = ''
    if extra_features:
        features_html += '<tr class="feature-sep-row"><td colspan="' + str(len(plans) + 2) + '" style="text-align:left; background:rgba(48,86,156,0.05); font-weight:700; color:var(--accent); font-size:11px; text-transform:uppercase; letter-spacing:0.05em; padding:8px 16px;">Características & Coberturas do Plano</td></tr>'
        for f in extra_features:
            label = f['label']
            if label.startswith('*'):
                continue
            tds = ''
            for v in f['values']:
                v_str = str(v)
                cls = 'cell-feature'
                if 'enfermaria' in v_str.lower():
                    cls = 'cell-enf-tag'
                elif 'apartamento' in v_str.lower():
                    cls = 'cell-apt-tag'
                elif 'nacional' in v_str.lower():
                    cls = 'cell-nac-tag'
                tds += f'<td class="{cls}">{v}</td>'
            features_html += f'<tr class="feature-row"><td><strong>{label}</strong></td><td class="cell-vidas">—</td>{tds}</tr>'
    
    return f'''<div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Faixa Etária</th>
            <th class="th-vidas">Vidas</th>
            {th_plans}
          </tr>
        </thead>
        <tbody>
          {tbody}
          {total_html}
          {features_html}
        </tbody>
      </table>
    </div>'''

# ── Generate insurer panels ──
def gen_insurer_panels(insurer_plans):
    panels = []
    for ins in insurer_plans:
        name = ins['name']
        plans = ins['plans']
        age_data = ins['age_data']
        section = ins['section'] or ''
        color = insurer_color(name)
        emoji = insurer_emoji(name)
        slug = insurer_slug(name)
        
        if not plans or not age_data:
            continue
            
        copar_text = 'Sem Coparticipação' if 'sem' in section.lower() else 'Com Coparticipação Parcial'
        copar_class = 'sem-copar' if 'sem' in section.lower() else 'copar-parcial'
        
        valid_totals = [t for t in (ins.get('total') or []) if isinstance(t, (int, float))]
        min_total = min(valid_totals) if valid_totals else None
        min_total_str = fmt_brl_compact(min_total) if min_total else '—'
        
        rede_html = get_rede_buttons(name)
        summary_cards = gen_insurer_summary_cards(ins)
        age_table = gen_age_table(ins)
        notes_card = gen_notes_card(ins)
        
        panels.append(f'''
        <!-- PANEL: {name} -->
        <div id="panel-{slug}" class="panel insurer-panel fade-in" style="display: none;">
          <!-- Company Header -->
          <div class="company-header" style="background:#fff; border:1px solid var(--border); border-radius:var(--radius); padding:0; display:flex; flex-direction:column; overflow:hidden; box-shadow:var(--shadow);">
            <div class="company-header-accent" style="height:5px; background:{color};"></div>
            <div class="company-header-content" style="display:flex; align-items:center; gap:24px; padding:24px 32px;">
              <div class="company-logo-circle" style="width:72px; height:56px; border-radius:8px; display:flex; align-items:center; justify-content:center; background:#fff; border:1px solid var(--border); padding:6px; flex-shrink:0; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
                {f'<img src="{get_logo_path(name)}" alt="{name}" style="max-width:100%; max-height:100%; object-fit:contain;">' if get_logo_path(name) else emoji}
              </div>
              <div class="company-info" style="flex:1;">
                <h2 style="font-size:22px; font-weight:800; color:var(--text-main); letter-spacing:-0.02em;">{name}</h2>
                <p style="font-size:12px; color:var(--text-muted); margin-top:4px; display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                  <span class="insurer-copar-tag tag-{'sem' if 'sem' in section.lower() else 'copar'}">
                    {'Sem Copart.' if 'sem' in section.lower() else 'Com Copart. Parcial'}
                  </span>
                  <span class="info-dot" style="width:4px; height:4px; border-radius:50%; background:var(--text-dim); display:inline-block;"></span>
                  <span>{len(plans)} planos</span>
                  <span class="info-dot" style="width:4px; height:4px; border-radius:50%; background:var(--text-dim); display:inline-block;"></span>
                  <span>{total_vidas} vidas</span>
                  <span class="info-dot" style="width:4px; height:4px; border-radius:50%; background:var(--text-dim); display:inline-block;"></span>
                  <span>{'Regional' if 'bronze' in name.lower() or 'smart' in name.lower() else 'Nacional'}</span>
                </p>
                {rede_html}
              </div>
              <div class="company-stats" style="display:flex; gap:8px; align-items:center;">
                <div class="stat-box">
                  <div class="sv">1</div>
                  <div class="sl">Modalidade</div>
                </div>
                <div class="stat-box">
                  <div class="sv">{len(plans)}</div>
                  <div class="sl">Planos</div>
                </div>
                <div class="stat-box stat-highlight" style="border-color:{color}30; background:{color}08;">
                  <div class="sv" style="color:{color};">{min_total_str}</div>
                  <div class="sl" style="color:{color};">Menor total/mês</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Filter bar (Enfermaria / Apartamento) -->
          <div class="filter-bar" style="display:flex; gap:24px; align-items:center; justify-content:flex-start; padding:14px 20px; background:#fff; border:1px solid var(--border); border-radius:var(--radius); margin-top:20px; box-shadow:var(--shadow);">
            <div class="filter-group" style="display:flex; flex-direction:column; gap:6px;">
              <div class="filter-label" style="font-size:10px; font-weight:800; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em;">Filtrar Acomodação</div>
              <div class="filter-buttons" style="display:flex; background:var(--bg-card2); padding:3px; border-radius:10px; border:1px solid var(--border);">
                <button class="filter-btn active" onclick="filterAcomodacao('{slug}', 'todos', this)">Todos</button>
                <button class="filter-btn" onclick="filterAcomodacao('{slug}', 'apartamento', this)">Apartamento</button>
                <button class="filter-btn" onclick="filterAcomodacao('{slug}', 'enfermaria', this)">Enfermaria</button>
              </div>
            </div>
          </div>

          <!-- Section Card -->
          <div class="section-card {copar_class}" style="background:#fff; border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; margin-top:20px; box-shadow:0 2px 12px rgba(48,86,156,0.04);">
            <div class="section-header" style="padding:18px 24px; background:rgba(48,86,156,0.03); border-bottom:1px solid var(--border); display:flex; align-items:center; gap:12px;">
              <div class="section-icon" style="background:{color}15; color:{color}; width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0;">
                {emoji}
              </div>
              <div>
                <div class="section-title" style="font-size:16px; font-weight:800; color:var(--text-main);">{copar_text}</div>
                <div class="section-subtitle" style="font-size:12px; color:var(--text-muted); margin-top:2px;">{len(plans)} planos disponíveis com tabelas completas por faixa etária</div>
              </div>
            </div>
            
            <!-- Plan summaries -->
            <div class="summary-grid" style="padding: 16px 20px;">
              {summary_cards}
            </div>

            <!-- Details Drawer -->
            <details class="age-drawer" open>
              <summary style="padding:14px 20px; font-size:13px; font-weight:600; color:var(--text-main); cursor:pointer; list-style:none; display:flex; align-items:center; gap:8px;">
                Visualizar tabela completa de preços por faixa etária e coberturas
              </summary>
              {age_table}
            </details>
          </div>

          <!-- Notes Card -->
          {notes_card}
        </div>
        ''')
    return '\n'.join(panels)

# ── Compute stats ──
titulares_total = rla_emp['titulares'] + rla_sub['titulares'] + rla_aura.get('titulares', 0)
dependentes_total = rla_emp['dependentes'] + rla_sub['dependentes'] + rla_aura.get('dependentes', 0)
vidas_total = rla_emp['total_vidas'] + rla_sub['total_vidas'] + rla_aura.get('total_vidas', 0)
premio_real_total = (rla_emp.get('premio_real') or 0) + (rla_sub.get('premio_real') or 0) + (rla_aura.get('premio_real') or 0)
iof_total = (rla_emp.get('iof') or 0) + (rla_sub.get('iof') or 0) + (rla_aura.get('iof') or 0)

# Per capita
per_capita = fatura_total / vidas_total if vidas_total else 0

# Reajuste previsto (Agosto)
reajuste_percentual = 15.87
fatura_reajuste = fatura_total * (1 + (reajuste_percentual / 100.0))

# ── Employees table HTML ──
show_unidade = (len(rla_sub.get('persons', [])) > 0) or (len(rla_aura.get('persons', [])) > 0)
unidade_th = '<th>Unidade</th>' if show_unidade else ''
employees_html = gen_employees_table(all_persons, show_unidade)

# ── Plan cards and insurer sections ──
insurer_panels_html = gen_insurer_panels(plans_excel)

# ── Nav items for sidebar ──
def gen_sidebar_items(insurer_plans):
    items = []
    for ins in insurer_plans:
        name = ins['name']
        plans = ins['plans']
        section = ins['section'] or ''
        color = insurer_color(name)
        emoji = insurer_emoji(name)
        slug = insurer_slug(name)
        if not plans:
            continue
        is_sem = 'sem' in section.lower()
        copar_badge = f'<span class="sidebar-badge badge-sem">Sem Copart</span>' if is_sem else f'<span class="sidebar-badge badge-copar">Com Copart</span>'
        logo_url = get_logo_path(name)
        logo_html = f'<img src="{logo_url}" alt="{name}" style="max-width:100%; max-height:100%; object-fit:contain;">' if logo_url else emoji
        items.append(f'''<button class="company-btn" id="btn-{slug}" onclick="showPanel('{slug}')">
          <div class="cb-icon" style="background:#fff; border:1px solid var(--border); overflow:hidden; display:flex; align-items:center; justify-content:center; padding:3px; flex-shrink:0;">
            {logo_html}
          </div>
          <span class="cb-name">{name}</span>
          {copar_badge}
          <span class="company-count">{len(plans)}</span>
        </button>''')
    return '\n'.join(items)

sidebar_items = gen_sidebar_items(plans_excel)

# ── Nav items for mobile select dropdown ──
def gen_mobile_select_options(insurer_plans):
    options = []
    for ins in insurer_plans:
        name = ins['name']
        plans = ins['plans']
        slug = insurer_slug(name)
        if not plans:
            continue
        options.append(f'<option value="{slug}">🏢 {name} ({len(plans)} planos)</option>')
    return '\n'.join(options)

mobile_select_options = gen_mobile_select_options(plans_excel)

# ── Build insurer list for JS ──
insurer_slugs_js = json.dumps([insurer_slug(i['name']) for i in plans_excel if i['plans']])

# ── FULL HTML ──────────────────────────────────────────────────────────────────

html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Estudo de Planos de Saúde – FRI Cosméticos | FBN RE</title>
  <meta name="description" content="Comparativo de planos de saúde empresariais para FRI Comércio de Cosméticos e Perfumaria. Análise de cenário atual Porto Saúde e alternativas Amil, Bradesco, SulAmérica, HapVida e Unimed." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />


  <style>
    :root {{
      --bg-dark:    #f4f7f9;
      --bg-card:    #ffffff;
      --bg-card2:   #f8fafd;
      --border:     rgba(48, 86, 156, 0.15);
      --accent:     #30569c;
      --accent2:    #1d3b73;
      --accent3:    #2ecb96;
      --accent4:    #e5a336;
      --text-main:  #1e293b;
      --text-muted: #64748b;
      --text-dim:   #94a3b8;
      --radius:     14px;
      --radius-sm:  8px;
      --shadow:     0 8px 32px rgba(48, 86, 156, 0.08);
      --transition: 0.22s cubic-bezier(0.4,0,0.2,1);
    }}

    html {{ scroll-behavior: smooth; }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    /* ─── MOBILE OPTIMIZATION ─── */
    @media (max-width: 900px) {{
      header {{
        position: sticky;
        top: 0;
        z-index: 120;
        height: 60px;
        padding: 0 16px;
        display: flex;
        align-items: center;
        justify-content: center;
      }}
      .header-inner {{
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        flex-direction: row;
      }}
      .header-title {{
        display: none !important;
      }}
      .logo-badge {{
        height: 38px;
        margin: 0 auto;
      }}
      .header-spacer {{
        display: none;
      }}
      .page-wrap {{
        grid-template-columns: 1fr;
        padding: 12px 12px 60px;
        gap: 16px;
      }}
      .sidebar {{
        display: none !important;
      }}
      .mobile-menu-container {{
        display: block;
        position: -webkit-sticky;
        position: sticky;
        top: 60px;
        z-index: 110;
        background: var(--bg-dark);
        padding: 8px 4px 12px;
        margin: -8px 0 8px 0;
      }}
      .mobile-select-cia {{
        width: 100%;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid var(--border);
        background: #fff;
        font-family: inherit;
        font-size: 14px;
        font-weight: 700;
        color: var(--accent);
        outline: none;
        box-shadow: 0 4px 12px rgba(48,86,156,0.06);
        appearance: none;
        -webkit-appearance: none;
        background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2330569c' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
        background-repeat: no-repeat;
        background-position: right 16px center;
        background-size: 16px;
      }}
      .scenario-hero-content {{ flex-direction: column; align-items: flex-start; gap: 20px; padding: 20px; }}
      .scenario-stats {{ margin-left: 0; width: 100%; justify-content: flex-start; gap: 8px; }}
      .stat-box {{ flex: 1 1 calc(50% - 8px); min-width: 0; padding: 12px 8px; }}
      .plan-cards {{ grid-template-columns: 1fr; gap: 16px; }}
      .summary-card {{ padding: 16px; }}
      .price-table {{ font-size: 11px; }}
      .price-table th, .price-table td {{ padding: 10px 6px; }}
      .table-wrap, .employees-table-wrap {{ overflow-x: auto; margin: 0 -12px; padding: 0 12px; }}
      .price-table-wrap {{ overflow-x: auto; margin: 0 -12px; padding: 0 12px; }}
      .savings-grid-layout {{ grid-template-columns: 1fr; gap: 12px; }}
      .savings-column[style*="grid-column: span 2;"] {{ grid-column: span 1 !important; }}
      .employees-header {{ flex-direction: column; align-items: stretch; gap: 12px; }}
      .search-input {{ width: 100%; }}
      .employees-table {{ min-width: 600px; }}
    }}

    body {{
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      min-height: 100vh;
      font-size: 14px;
      line-height: 1.55;
    }}

    /* ─── HEADER ─── */
    header {{
      background: #fff;
      padding: 0 32px;
      position: sticky; top: 0; z-index: 100;
      box-shadow: 0 1px 0 var(--border), 0 4px 20px rgba(48,86,156,0.06);
    }}
    .header-inner {{
      max-width: 1440px; margin: 0 auto;
      display: flex; align-items: center; gap: 16px; height: 64px;
    }}
    .logo-badge {{ height: 48px; display: flex; align-items: center; }}
    .logo-badge img {{ height: 100%; object-fit: contain; }}
    .header-title h1 {{ font-size: 16px; font-weight: 700; color: var(--text-main); line-height: 1.2; }}
    .header-title p {{ font-size: 11px; color: var(--text-muted); }}
    .header-spacer {{ flex: 1; }}
    .header-badge {{
      background: rgba(46,203,150,0.1); border: 1px solid rgba(46,203,150,0.25);
      color: var(--accent3); border-radius: 20px; padding: 4px 12px;
      font-size: 11px; font-weight: 600;
    }}

    /* ─── LAYOUT ─── */
    .page-wrap {{
      max-width: 1440px; margin: 0 auto;
      padding: 40px 48px 80px;
      display: grid; grid-template-columns: 280px 1fr; gap: 40px;
      align-items: start;
    }}

    /* ─── SIDEBAR ─── */
    .sidebar {{
      position: sticky; top: 80px;
      display: flex; flex-direction: column; gap: 8px;
      max-height: calc(100vh - 100px); overflow-y: auto;
      padding: 24px; background: var(--bg-card);
      border: 1px solid rgba(48,86,156,0.1); border-radius: 20px;
      box-shadow: 0 12px 32px rgba(48,86,156,0.06);
    }}
    .sidebar::-webkit-scrollbar {{ width: 4px; }}
    .sidebar-label {{
      font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
      color: var(--text-dim); text-transform: uppercase;
      padding: 0 4px 6px; border-bottom: 1px solid var(--border); margin-bottom: 4px;
    }}
    .sidebar-section {{ margin-top: 8px; }}
    .company-btn {{
      display: flex; align-items: center; gap: 10px;
      padding: 10px 12px; border-radius: var(--radius-sm);
      border: 1px solid transparent; background: transparent;
      color: var(--text-muted); cursor: pointer;
      transition: all var(--transition);
      text-align: left; width: 100%;
      font-family: inherit; font-size: 13px; font-weight: 500;
    }}
    .company-btn:hover {{ background: var(--bg-card2); color: var(--text-main); border-color: var(--border); }}
    .company-btn.active {{
      background: linear-gradient(135deg, rgba(48,86,156,0.1), rgba(48,86,156,0.06));
      border-color: rgba(48,86,156,0.25); color: var(--accent);
    }}
    .cb-icon {{
      width: 36px; height: 36px; border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 16px; flex-shrink: 0;
    }}
    .cb-name {{ flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 600; }}
    .company-count {{
      background: rgba(0,0,0,0.05); border-radius: 10px;
      padding: 2px 8px; font-size: 10px; font-weight: 600; color: var(--text-dim);
    }}
    .company-btn.active .company-count {{ background: rgba(48,86,156,0.12); color: var(--accent); }}

    .sidebar-divider {{ height: 1px; background: var(--border); margin: 6px 0; }}
    .sidebar-special-btn {{
      display: flex; align-items: center; gap: 10px;
      padding: 10px 12px; border-radius: var(--radius-sm);
      border: 1px solid rgba(46,203,150,0.2);
      background: linear-gradient(135deg, rgba(46,203,150,0.06), rgba(46,203,150,0.03));
      color: var(--accent3); cursor: pointer;
      transition: all var(--transition);
      text-align: left; width: 100%;
      font-family: inherit; font-size: 13px; font-weight: 600;
    }}
    .sidebar-special-btn:hover {{
      border-color: rgba(46,203,150,0.4);
      background: linear-gradient(135deg, rgba(46,203,150,0.12), rgba(46,203,150,0.06));
    }}
    .sidebar-special-btn.active {{
      background: linear-gradient(135deg, rgba(46,203,150,0.15), rgba(46,203,150,0.08));
      border-color: rgba(46,203,150,0.4);
    }}

    /* ─── MAIN CONTENT ─── */
    .main-content {{ display: flex; flex-direction: column; gap: 32px; min-width: 0; overflow: hidden; }}

    /* ─── SCENARIO ATUAL HERO ─── */
    .scenario-hero {{
      background: var(--bg-card); border: 1px solid var(--border);
      border-radius: var(--radius); overflow: hidden;
      box-shadow: var(--shadow);
    }}
    .scenario-hero-accent {{
      height: 5px;
      background: linear-gradient(90deg, #e63050 0%, #e5a336 50%, var(--accent3) 100%);
    }}
    .scenario-hero-content {{
      display: flex; align-items: center; gap: 28px; padding: 28px 32px;
    }}
    .scenario-logo {{
      width: 64px; height: 64px; border-radius: 14px;
      background: linear-gradient(135deg, #e63050, #c0392b);
      display: flex; align-items: center; justify-content: center;
      font-size: 26px; flex-shrink: 0;
      box-shadow: 0 4px 16px rgba(230,48,80,0.25);
    }}
    .scenario-info h2 {{
      font-size: 22px; font-weight: 800; color: var(--text-main);
      letter-spacing: -0.02em;
    }}
    .scenario-info .sub {{
      font-size: 12px; color: var(--text-muted); margin-top: 4px;
      display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    }}
    .scenario-info .sub .dot {{ width: 3px; height: 3px; border-radius: 50%; background: var(--text-dim); }}
    .scenario-atual-badge {{
      display: inline-flex; align-items: center; gap: 5px;
      background: rgba(230,48,80,0.1); border: 1px solid rgba(230,48,80,0.2);
      color: #e63050; border-radius: 20px; padding: 3px 10px;
      font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
    }}
    .scenario-stats {{ margin-left: auto; display: flex; gap: 10px; flex-wrap: wrap; }}
    .stat-box {{
      text-align: center; display: flex; flex-direction: column; align-items: center;
      background: var(--bg-card2); border: 1px solid var(--border);
      border-radius: 12px; padding: 14px 20px; min-width: 90px;
      transition: all 0.2s ease;
    }}
    .stat-box:hover {{ border-color: rgba(48,86,156,0.3); box-shadow: 0 2px 8px rgba(48,86,156,0.08); }}
    .stat-box .sv {{ font-size: 20px; font-weight: 800; color: var(--accent); line-height: 1; }}
    .stat-box .sl {{ font-size: 9px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px; }}
    .stat-box.stat-warn {{ background: linear-gradient(135deg, rgba(230,48,80,0.06), rgba(230,48,80,0.1)); border-color: rgba(230,48,80,0.25); }}
    .stat-box.stat-warn .sv {{ color: #e63050; }}
    .stat-box.stat-green {{ background: linear-gradient(135deg, rgba(46,203,150,0.06), rgba(46,203,150,0.1)); border-color: rgba(46,203,150,0.25); }}
    .stat-box.stat-green .sv {{ color: var(--accent3); }}

    /* ─── TABS ─── */
    .tabs-bar {{
      display: flex; gap: 4px;
      background: var(--bg-card); border: 1px solid var(--border);
      border-radius: var(--radius-sm); padding: 4px; width: fit-content;
    }}
    .tab-btn {{
      padding: 7px 18px; border-radius: 6px; border: none;
      background: transparent; color: var(--text-muted);
      font-family: inherit; font-size: 12px; font-weight: 600;
      cursor: pointer; transition: all var(--transition);
      display: flex; align-items: center; gap: 6px;
    }}
    .tab-btn.active {{ background: var(--accent); color: #fff; }}
    .tab-btn:not(.active):hover {{ background: var(--bg-card2); color: var(--text-main); }}

    /* ─── PANEL ─── */
    .panel {{ display: none; }}
    .panel.active {{ display: block; }}

    /* ─── EMPLOYEES TABLE ─── */
    .employees-section {{
      background: var(--bg-card); border: 1px solid var(--border);
      border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow);
    }}
    .employees-header {{
      padding: 20px 24px; border-bottom: 1px solid var(--border);
      background: rgba(48,86,156,0.02);
      display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
    }}
    .employees-header h3 {{
      font-size: 15px; font-weight: 700; color: var(--text-main);
      display: flex; align-items: center; gap: 8px;
    }}
    .employees-search {{
      display: flex; align-items: center; gap: 8px;
    }}
    .search-input {{
      border: 1px solid var(--border); border-radius: 8px;
      padding: 6px 12px; font-family: inherit; font-size: 12px;
      background: var(--bg-card2); color: var(--text-main);
      outline: none; transition: border-color 0.2s;
      width: 200px;
    }}
    .search-input:focus {{ border-color: var(--accent); }}
    .employees-table-wrap {{ overflow-x: auto; }}
    .employees-table {{
      width: 100%; border-collapse: collapse; font-size: 12.5px;
    }}
    .employees-table th {{
      padding: 10px 14px; text-align: left;
      font-weight: 600; color: var(--text-muted); font-size: 11px;
      letter-spacing: 0.04em; border-bottom: 1px solid var(--border);
      background: var(--bg-card2); white-space: nowrap;
    }}
    .employees-table td {{
      padding: 9px 14px; border-bottom: 1px solid rgba(0,0,0,0.04);
      color: var(--text-muted);
    }}
    .employees-table tr:hover td {{ background: rgba(0,0,0,0.02); }}
    .employees-table .td-name {{ color: var(--text-main); font-weight: 500; white-space: nowrap; }}
    .employees-table .td-plan {{ color: var(--accent); font-weight: 500; white-space: nowrap; }}
    .employees-table .td-valor {{ color: var(--text-main); font-weight: 600; text-align: right; white-space: nowrap; }}
    .employees-table .td-inicio {{ color: var(--text-muted); font-size: 11px; white-space: nowrap; }}
    .employees-table .td-unidade {{ color: var(--text-muted); font-size: 11px; }}
    .person-badge {{
      display: inline-flex; align-items: center; justify-content: center;
      width: 18px; height: 18px; border-radius: 4px;
      font-size: 9px; font-weight: 700;
    }}
    .badge-titular {{ background: rgba(48,86,156,0.15); color: var(--accent); }}
    .badge-dep {{ background: rgba(229,163,54,0.15); color: var(--accent4); }}

    .employees-footer {{
      padding: 12px 24px; border-top: 1px solid var(--border);
      background: rgba(48,86,156,0.02);
      display: flex; align-items: center; justify-content: space-between;
      font-size: 12px; color: var(--text-muted);
    }}

    /* ─── UNIDADES INFO ─── */
    .unidades-grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px;
    }}
    .unidade-card {{
      background: var(--bg-card); border: 1px solid var(--border);
      border-radius: var(--radius); overflow: hidden;
      box-shadow: 0 2px 8px rgba(48,86,156,0.05);
    }}
    .unidade-card-header {{
      padding: 16px 20px; border-bottom: 1px solid var(--border);
      background: rgba(48,86,156,0.02);
      display: flex; align-items: center; gap: 10px;
    }}
    .unidade-icon {{
      width: 32px; height: 32px; border-radius: 8px;
      background: rgba(48,86,156,0.1); color: var(--accent);
      display: flex; align-items: center; justify-content: center;
      font-size: 14px; flex-shrink: 0;
    }}
    .unidade-name {{ font-size: 13px; font-weight: 700; color: var(--text-main); }}
    .unidade-sub {{ font-size: 11px; color: var(--text-muted); }}
    .unidades-grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px;
    }}
    .unidade-card {{
      background: var(--bg-card); border: 1px solid var(--border);
      border-radius: var(--radius); overflow: hidden;
      box-shadow: 0 2px 8px rgba(48,86,156,0.05);
    }}
    .unidade-card-header {{
      padding: 16px 20px; border-bottom: 1px solid var(--border);
      background: rgba(48,86,156,0.02);
      display: flex; align-items: center; gap: 10px;
    }}
    .unidade-icon {{
      width: 32px; height: 32px; border-radius: 8px;
      background: rgba(48,86,156,0.1); color: var(--accent);
      display: flex; align-items: center; justify-content: center;
      font-size: 14px; flex-shrink: 0;
    }}
    .unidade-name {{ font-size: 13px; font-weight: 700; color: var(--text-main); }}
    .unidade-sub {{ font-size: 11px; color: var(--text-muted); }}
    .unidade-stats {{
      padding: 16px 20px;
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
    }}
    .unidade-stat {{ text-align: center; }}
    .unidade-stat .usv {{ font-size: 18px; font-weight: 800; color: var(--accent); }}
    .unidade-stat .usl {{ font-size: 9px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }}
    .unidade-stat.highlight .usv {{ color: #e63050; }}

    /* ─── INSURER SUMMARY CARDS ─── */
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 12px;
      padding: 16px 20px;
    }}
    .summary-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 14px;
      transition: all 0.22s ease;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      box-shadow: 0 2px 6px rgba(48,86,156,0.03);
    }}
    .summary-card:hover {{
      border-color: rgba(48,86,156,0.35);
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(48,86,156,0.08);
    }}
    .summary-card .plan-name {{
      font-size: 12px; font-weight: 700; color: var(--text-main);
      margin-bottom: 4px;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .summary-card .acomodacao-tag {{
      font-size: 10px; color: var(--text-muted);
      display: inline-flex; align-items: center; gap: 4px;
      margin-bottom: 8px;
    }}
    .tag-enf {{
      background: rgba(255,165,0,0.12);
      color: #f5a623;
      border-radius: 4px; padding: 1px 6px; font-size: 9px; font-weight: 700;
    }}
    .tag-apt {{
      background: rgba(48,86,156,0.12);
      color: var(--accent);
      border-radius: 4px; padding: 1px 6px; font-size: 9px; font-weight: 700;
    }}
    .summary-card .total-value {{
      font-size: 17px; font-weight: 800;
      color: var(--text-main);
      letter-spacing: -0.02em;
    }}
    .summary-card .total-label {{
      font-size: 10px; color: var(--text-muted); margin-top: 2px;
    }}
    .summary-card.best-value {{
      border-color: rgba(46,203,150,0.4);
      background: linear-gradient(135deg, rgba(46,203,150,0.05) 0%, var(--bg-card) 60%);
    }}
    .best-badge {{
      display: inline-flex; align-items: center; gap: 4px;
      font-size: 9px; font-weight: 700; color: var(--accent3);
      background: rgba(46,203,150,0.12);
      border-radius: 4px; padding: 1px 6px;
      margin-bottom: 8px;
    }}

    /* ─── SIDEBAR BADGES ─── */
    .sidebar-badge {{
      font-size: 8.5px;
      font-weight: 700;
      border-radius: 4px;
      padding: 1px 4px;
      margin-left: 6px;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      white-space: nowrap;
    }}
    .sidebar-badge.badge-sem {{
      background: rgba(46,203,150,0.12);
      color: var(--accent3);
    }}
    .sidebar-badge.badge-copar {{
      background: rgba(229,163,54,0.12);
      color: var(--accent4);
    }}

    /* ─── TABLE VIDAS COLUMN & FEATURES ─── */
    .cell-vidas {{
      text-align: center;
      font-weight: 600;
      color: var(--text-muted);
    }}
    .th-vidas {{
      text-align: center;
      color: var(--text-muted);
      font-size: 11px;
    }}
    .cell-enf-tag {{
      color: #f5a623 !important;
      font-weight: 600;
      text-align: right;
    }}
    .cell-apt-tag {{
      color: var(--accent) !important;
      font-weight: 600;
      text-align: right;
    }}
    .cell-nac-tag {{
      color: var(--accent3) !important;
      font-weight: 600;
      text-align: right;
    }}
    .feature-row td {{
      padding: 9px 16px;
      border-bottom: 1px solid rgba(0,0,0,0.03);
      font-size: 12px;
      color: var(--text-main);
    }}
    .feature-row td:first-child {{
      color: var(--text-muted) !important;
    }}
    .feature-sep-row td {{
      border-top: 1.5px solid var(--border);
      border-bottom: 1.5px solid var(--border);
    }}

    /* ─── NOTES/DIFERENCIAIS BOX ─── */
    .diferenciais-box {{
      margin-top: 24px;
      background: linear-gradient(135deg, rgba(48,86,156,0.03) 0%, rgba(46,203,150,0.03) 100%);
      border: 1px solid rgba(48,86,156,0.12);
      border-radius: var(--radius);
      padding: 20px 24px;
      border-left: 4px solid var(--accent);
      box-shadow: var(--shadow);
    }}
    .diferenciais-title {{
      font-size: 14px;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .diferenciais-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .diferenciais-list li {{
      position: relative;
      padding-left: 16px;
      color: var(--text-muted);
      font-size: 12.5px;
      line-height: 1.5;
    }}
    .diferenciais-list li::before {{
      content: '•';
      position: absolute;
      left: 0;
      color: var(--accent);
      font-weight: bold;
    }}

    /* ─── COMPANY HEADER ─── */
    .company-header-content p span {{
      display: inline-flex;
      align-items: center;
    }}
    .btn-rede {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: linear-gradient(135deg, rgba(48,86,156,0.06), rgba(48,86,156,0.12));
      border: 1px solid rgba(48,86,156,0.15);
      color: var(--accent);
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      text-decoration: none;
    }}
    .btn-rede:hover {{
      background: linear-gradient(135deg, rgba(48,86,156,0.12), rgba(48,86,156,0.2));
      box-shadow: 0 2px 8px rgba(48,86,156,0.15);
      transform: translateY(-1px);
    }}
    .tag-sem {{
      background: rgba(46,203,150,0.12);
      color: var(--accent3);
      font-size: 9px;
      font-weight: 700;
      border-radius: 4px;
      padding: 1px 6px;
    }}
    .tag-copar {{
      background: rgba(229,163,54,0.12);
      color: var(--accent4);
      font-size: 9px;
      font-weight: 700;
      border-radius: 4px;
      padding: 1px 6px;
    }}

    /* ─── TABLE ─── */
    .table-wrap {{ overflow-x: auto; padding: 0 0 2px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; white-space: nowrap; }}
    thead tr {{ background: var(--bg-card2); }}
    th {{
      padding: 10px 16px; text-align: right;
      font-weight: 600; color: var(--text-muted);
      font-size: 11px; letter-spacing: 0.04em;
      border-bottom: 1px solid var(--border);
    }}
    th:first-child {{ text-align: left; }}
    .th-plan {{ color: var(--text-main); font-size: 12px; font-weight: 700; }}
    .th-apt {{ color: var(--accent); }}
    tbody tr {{ border-bottom: 1px solid rgba(0,0,0,0.04); transition: background var(--transition); }}
    tbody tr:hover {{ background: rgba(0,0,0,0.025); }}
    tbody tr.total-row {{
      background: rgba(48,86,156,0.05); border-top: 2px solid rgba(48,86,156,0.2); border-bottom: none;
    }}
    tbody tr.total-row td {{ font-weight: 700; color: var(--text-main); font-size: 13px; }}
    td {{ padding: 9px 16px; text-align: right; color: var(--text-muted); }}
    td:first-child {{ text-align: left; color: var(--text-main); font-weight: 500; }}
    .cell-value {{ color: var(--text-main); }}
    .cell-best {{ color: var(--accent3); font-weight: 700; position: relative; }}
    .cell-best::after {{ content: '★'; font-size: 8px; vertical-align: super; margin-left: 2px; opacity: 0.6; }}

    /* ─── ANIMATIONS ─── */
    @keyframes fadeInUp {{
      from {{ opacity: 0; transform: translateY(16px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .fade-in {{ animation: fadeInUp 0.35s ease both; }}



    /* ─── SCROLLBAR ─── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(48,86,156,0.15); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(48,86,156,0.3); }}

    /* ─── RESPONSIVE ─── */
    @media (max-width: 1100px) {{
      .page-wrap {{ grid-template-columns: 220px 1fr; gap: 20px; }}
      .scenario-hero-content {{ flex-wrap: wrap; }}
      .scenario-stats {{ margin-left: 0; margin-top: 8px; }}
    }}
    @media (max-width: 900px) {{
      /* Mobile layout consolidated in optimization section above */
    }}
    @media (max-width: 600px) {{
      .scenario-hero-content {{ padding: 20px; gap: 16px; }}
      .unidades-grid {{ grid-template-columns: 1fr; }}
      .tabs-bar {{ width: 100%; }}
      .tab-btn {{ flex: 1; justify-content: center; font-size: 11px; padding: 6px 10px; }}
    }}

    /* ─── FILTER BUTTONS ─── */
    .filter-btn {{
      padding: 6px 14px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      border-radius: 8px;
      transition: all var(--transition);
      outline: none;
    }}
    .filter-btn.active {{
      background: var(--bg-card);
      color: var(--accent);
      box-shadow: 0 2px 6px rgba(48,86,156,0.08);
      border: 1px solid rgba(48,86,156,0.1);
    }}
    .filter-btn:not(.active):hover {{
      color: var(--text-main);
    }}

    /* ─── SAVINGS SIMULATOR ─── */
    .savings-simulator {{
      margin: 8px 20px 20px;
      animation: fadeInUp 0.3s ease both;
      display: none;
    }}
    .savings-card {{
      border-radius: var(--radius-sm);
      padding: 16px 20px;
      border: 1px solid var(--border);
      position: relative;
      box-shadow: 0 4px 16px rgba(48,86,156,0.04);
      background: #fff;
      text-align: left;
    }}
    .savings-positive {{
      background: linear-gradient(135deg, rgba(46,203,150,0.06) 0%, rgba(255,255,255,0.9) 100%);
      border-color: rgba(46,203,150,0.25);
      border-left: 5px solid var(--accent3);
    }}
    .savings-negative {{
      background: linear-gradient(135deg, rgba(229,163,54,0.06) 0%, rgba(255,255,255,0.9) 100%);
      border-color: rgba(229,163,54,0.25);
      border-left: 5px solid var(--accent4);
    }}
    .savings-neutral {{
      background: var(--bg-card2);
      border-left: 5px solid var(--accent);
    }}
    .savings-badge-label {{
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      margin-bottom: 12px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .savings-grid-layout {{
      display: grid;
      grid-template-columns: 2fr 1.5fr 1.5fr;
      gap: 16px;
      align-items: center;
    }}
    .savings-column {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .savings-label {{
      font-size: 9px;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .savings-value-plan {{
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-main);
    }}
    .savings-value-monthly {{
      font-size: 15px;
      font-weight: 800;
      color: var(--text-main);
    }}
    .savings-value-annual {{
      font-size: 19px;
      font-weight: 900;
      color: var(--accent3);
      letter-spacing: -0.02em;
    }}
    .savings-footer-text {{
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid rgba(46,203,150,0.12);
      font-size: 11.5px;
      color: #1e7052;
      line-height: 1.45;
    }}
    /* Style for selected summary card */
    .summary-card.selected-plan {{
      border-color: var(--accent) !important;
      background: linear-gradient(135deg, rgba(48,86,156,0.05) 0%, var(--bg-card) 60%) !important;
      box-shadow: 0 4px 16px rgba(48,86,156,0.12) !important;
    }}
    .summary-card.selected-plan::after {{
      content: '✓';
      position: absolute;
      top: 6px;
      right: 10px;
      color: var(--accent);
      font-weight: 900;
      font-size: 12px;
    }}
    .mobile-menu-container {{
      display: none;
    }}
  </style>
</head>

<body>

<!-- ─── HEADER ─── -->
<header>
  <div class="header-inner">
    <div class="logo-badge" style="height:48px; display:flex; align-items:center;">
      <img src="../assets/logos/Logo-FBN-azul.png" alt="FBN RE" style="height:100%; object-fit:contain;">
    </div>
    <div class="header-title">
      <h1>Estudo de Planos de Saúde</h1>
      <p>FRI Comércio de Cosméticos e Perfumaria · Competência {competencia}</p>
    </div>
    <div class="header-spacer"></div>
  </div>
</header>

<!-- ─── MAIN LAYOUT ─── -->
<div class="page-wrap">

  <!-- ─── SIDEBAR ─── -->
  <aside class="sidebar">
    <div class="sidebar-label">Cotações por Seguradora</div>

    <button class="sidebar-special-btn active" id="btn-rla" onclick="showPanel('rla')">
      <div class="cb-icon" style="background:#fff; border:1px solid rgba(48,86,156,0.15); overflow:hidden; display:flex; align-items:center; justify-content:center; padding:3px; flex-shrink:0;">
        <img src="../assets/logos/logo-porto-saude.png" alt="Porto Saúde" style="max-width:100%; max-height:100%; object-fit:contain;">
      </div>
      <span class="cb-name">Cenário Atual (Porto)</span>
    </button>

    <div class="sidebar-divider"></div>
    <div class="sidebar-label sidebar-section">Alternativas</div>

    {sidebar_items}
  </aside>

  <!-- ─── CONTENT ─── -->
  <main class="main-content">

    <!-- Mobile dropdown selector -->
    <div class="mobile-menu-container">
      <select class="mobile-select-cia" id="mobile-insurer-select" onchange="showPanel(this.value)">
        <option value="rla">🔍 Cenário Atual (Porto Saúde)</option>
        {mobile_select_options}
      </select>
    </div>

    <!-- ─── SCENARIO ATUAL HERO ─── -->
    <div class="scenario-hero">
      <div class="scenario-hero-accent"></div>
      <div class="scenario-hero-content">
        <div class="scenario-logo" style="width:72px; height:64px; border-radius:8px; display:flex; align-items:center; justify-content:center; background:#fff; border:1px solid var(--border); padding:6px; flex-shrink:0; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.04);">
          <img src="lenvie-logo.svg" alt="L'Envie / FRI Cosméticos" style="max-width:100%; max-height:100%; object-fit:contain;">
        </div>
        <div class="scenario-info">
          <h2>FRI Comércio de Cosméticos e Perfumaria</h2>
          <div class="sub">
            <span class="scenario-atual-badge">📌 Cenário Atual</span>
            <span class="dot"></span>
            <span>Porto Saúde S.A.</span>
            <span class="dot"></span>
            <span>Fatura {competencia}</span>
          </div>
          <div style="margin-top: 8px; font-size: 12px; color: var(--text-muted);">
            3 unidades: <strong>FRI COMERCIO DE COSMETICOS E PERFUMARIA</strong> + <strong>KCB SERVICOS DE APOIO ADM.</strong> + <strong>AURA COSMETICOS E PERFUMARIA</strong>
          </div>
        </div>
        <div class="scenario-stats">
          <div class="stat-box" style="background: rgba(48,86,156,0.04);">
            <div class="sv" style="font-size: 16px;">{fmt_brl_compact(fatura_total)}</div>
            <div class="sl">Fatura Atual</div>
          </div>
          <div class="stat-box stat-warn" style="position: relative;">
            <div class="sv" style="font-size: 20px; color: #e63050;">{fmt_brl_compact(fatura_reajuste)}</div>
            <div class="sl">Fatura c/ Reajuste</div>
            <div style="position: absolute; top: -8px; right: -8px; background: #e63050; color: #fff; font-size: 9px; padding: 2px 6px; border-radius: 10px; font-weight: bold; box-shadow: 0 2px 6px rgba(230,48,80,0.3);">+15,87% (Ago)</div>
          </div>
          <div class="stat-box">
            <div class="sv">{vidas_total}</div>
            <div class="sl">Total Vidas</div>
          </div>
          <div class="stat-box">
            <div class="sv">{titulares_total}</div>
            <div class="sl">Titulares</div>
          </div>
          <div class="stat-box">
            <div class="sv">{dependentes_total}</div>
            <div class="sl">Dependentes</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── PANELS ─── -->

    <!-- PANEL: RLA / Cenário Atual -->
    <div id="panel-rla" class="panel active">

      <!-- Tabs -->
      <div class="tabs-bar">
        <button class="tab-btn active" id="tab-vidas" onclick="showTab('vidas')">👥 Relação de Vidas</button>
        <button class="tab-btn" id="tab-unidades" onclick="showTab('unidades')">🏢 Por Unidade</button>
      </div>

      <!-- Sub-panel: Vidas -->
      <div id="tabpanel-vidas" class="panel active">
        <div class="employees-section fade-in" style="margin-top: 16px;">
          <div class="employees-header">
            <h3>📋 Relação Atualizada de Vidas — {competencia}</h3>
            <div class="employees-search">
              <input type="text" class="search-input" id="emp-search" placeholder="Buscar funcionário..." oninput="filterEmployees()">
            </div>
          </div>
          <div class="employees-table-wrap">
            <table class="employees-table" id="emp-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  {'<th>Unidade</th>' if show_unidade else ''}
                  <th>Plano Atual</th>
                  <th>Início Vigência</th>
                  <th style="text-align:right">Valor Mensal</th>
                </tr>
              </thead>
              <tbody id="emp-tbody">
                {employees_html}
              </tbody>
            </table>
          </div>
          <div class="employees-footer">
            <span id="emp-count">{len(all_persons)} pessoas</span>
            <span style="font-weight:600; color:var(--accent)">Total: {fmt_brl_compact(fatura_total)}</span>
          </div>
        </div>
      </div>

      <!-- Sub-panel: Por Unidade -->
      <div id="tabpanel-unidades" class="panel">
        <div class="unidades-grid" style="margin-top: 16px;">

          <!-- Unidade 1: FRI Principal -->
          <div class="unidade-card fade-in">
            <div class="unidade-card-header">
              <div class="unidade-icon">🏭</div>
              <div>
                <div class="unidade-name">FRI COMERCIO DE COSMETICOS</div>
                <div class="unidade-sub">Estipulante principal · Subestipulante 1873213</div>
              </div>
            </div>
            <div class="unidade-stats">
              <div class="unidade-stat">
                <div class="usv">{rla_emp['titulares']}</div>
                <div class="usl">Titulares</div>
              </div>
              <div class="unidade-stat">
                <div class="usv">{rla_emp['dependentes']}</div>
                <div class="usl">Dependentes</div>
              </div>
              <div class="unidade-stat">
                <div class="usv">{rla_emp['total_vidas']}</div>
                <div class="usl">Total Vidas</div>
              </div>
              <div class="unidade-stat highlight" style="grid-column: 1 / -1; border-top: 1px solid var(--border); padding-top: 12px; margin-top: 4px;">
                <div class="usv">{fmt_brl_compact(rla_emp['invoice_total'])}</div>
                <div class="usl">Fatura {competencia}</div>
              </div>
            </div>
          </div>

          <!-- Unidade 2: KCB Subestipulante -->
          <div class="unidade-card fade-in">
            <div class="unidade-card-header">
              <div class="unidade-icon">🏢</div>
              <div>
                <div class="unidade-name">KCB SERVICOS DE APOIO ADM.</div>
                <div class="unidade-sub">Subestipulante · Fatura {competencia}</div>
              </div>
            </div>
            <div class="unidade-stats">
              <div class="unidade-stat">
                <div class="usv">{rla_sub['titulares']}</div>
                <div class="usl">Titulares</div>
              </div>
              <div class="unidade-stat">
                <div class="usv">{rla_sub['dependentes']}</div>
                <div class="usl">Dependentes</div>
              </div>
              <div class="unidade-stat">
                <div class="usv">{rla_sub['total_vidas']}</div>
                <div class="usl">Total Vidas</div>
              </div>
              <div class="unidade-stat highlight" style="grid-column: 1 / -1; border-top: 1px solid var(--border); padding-top: 12px; margin-top: 4px;">
                <div class="usv">{fmt_brl_compact(rla_sub['invoice_total'])}</div>
                <div class="usl">Fatura {competencia}</div>
              </div>
            </div>
          </div>

          <!-- Unidade 3: Aura Cosmeticos -->
          <div class="unidade-card fade-in">
            <div class="unidade-card-header">
              <div class="unidade-icon">✨</div>
              <div>
                <div class="unidade-name">AURA COSMETICOS E PERFUMARIA</div>
                <div class="unidade-sub">Subestipulante · CNPJ 49.532.571/0001-66 · Fatura {competencia}</div>
              </div>
            </div>
            <div class="unidade-stats">
              <div class="unidade-stat">
                <div class="usv">{rla_aura.get('titulares', 0)}</div>
                <div class="usl">Titulares</div>
              </div>
              <div class="unidade-stat">
                <div class="usv">{rla_aura.get('dependentes', 0)}</div>
                <div class="usl">Dependentes</div>
              </div>
              <div class="unidade-stat">
                <div class="usv">{rla_aura.get('total_vidas', 0)}</div>
                <div class="usl">Total Vidas</div>
              </div>
              <div class="unidade-stat highlight" style="grid-column: 1 / -1; border-top: 1px solid var(--border); padding-top: 12px; margin-top: 4px;">
                <div class="usv">{fmt_brl_compact(rla_aura.get('invoice_total', 0))}</div>
                <div class="usl">Fatura {competencia}</div>
              </div>
            </div>
          </div>

          <!-- Combined -->
          <div class="unidade-card fade-in" style="border-color: rgba(46,203,150,0.3); background: linear-gradient(135deg, rgba(46,203,150,0.03), var(--bg-card));">
            <div class="unidade-card-header" style="background: rgba(46,203,150,0.04);">
              <div class="unidade-icon" style="background: rgba(46,203,150,0.15); color: var(--accent3);">📊</div>
              <div>
                <div class="unidade-name" style="color: var(--accent3)">CONSOLIDADO GERAL</div>
                <div class="unidade-sub">Empresa + 2 Subestipulantes</div>
              </div>
            </div>
            <div class="unidade-stats">
              <div class="unidade-stat">
                <div class="usv" style="color: var(--accent3)">{titulares_total}</div>
                <div class="usl">Titulares</div>
              </div>
              <div class="unidade-stat">
                <div class="usv" style="color: var(--accent3)">{dependentes_total}</div>
                <div class="usl">Dependentes</div>
              </div>
              <div class="unidade-stat">
                <div class="usv" style="color: var(--accent3)">{vidas_total}</div>
                <div class="usl">Total Vidas</div>
              </div>
              <div class="unidade-stat" style="grid-column: 1 / -1; border-top: 1px solid var(--border); padding-top: 12px; margin-top: 4px;">
                <div class="usv" style="color: #e63050">{fmt_brl_compact(fatura_total)}</div>
                <div class="usl">Fatura Total {competencia}</div>
              </div>
            </div>
          </div>

        </div>
      </div>

    </div><!-- /panel-rla -->

    <!-- DYNAMIC INSURER PANELS -->
    {insurer_panels_html}

  </main>
</div>

<script>
const INSURER_SLUGS = {insurer_slugs_js};
let currentPanel = 'rla';
let currentTab = 'vidas';

function showPanel(panelId) {{
  // Hide all panels
  document.getElementById('panel-rla').style.display = 'none';
  document.getElementById('panel-rla').classList.remove('active');
  
  INSURER_SLUGS.forEach(slug => {{
    const p = document.getElementById('panel-' + slug);
    if (p) {{
      p.style.display = 'none';
      p.classList.remove('active');
    }}
  }});

  // Update active states on sidebar buttons
  document.getElementById('btn-rla').classList.remove('active');
  INSURER_SLUGS.forEach(slug => {{
    const btn = document.getElementById('btn-' + slug);
    if (btn) btn.classList.remove('active');
  }});

  // Show active panel
  if (panelId === 'rla') {{
    document.getElementById('panel-rla').style.display = 'block';
    document.getElementById('panel-rla').classList.add('active');
    document.getElementById('btn-rla').classList.add('active');
    currentPanel = 'rla';
  }} else {{
    const p = document.getElementById('panel-' + panelId);
    if (p) {{
      p.style.display = 'block';
      p.classList.add('active');
    }}
    const btn = document.getElementById('btn-' + panelId);
    if (btn) btn.classList.add('active');
    currentPanel = 'insurer';
  }}
  
  // Sync the mobile select value if it exists
  const mobileSelect = document.getElementById('mobile-insurer-select');
  if (mobileSelect) {{
    mobileSelect.value = panelId;
  }}
  
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function filterAcomodacao(insurerSlug, type, btn) {{
  // Update active button state
  const btnGroup = btn.parentElement;
  btnGroup.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  const panel = document.getElementById('panel-' + insurerSlug);
  if (!panel) return;

  // Filter summary cards
  const cards = panel.querySelectorAll('.summary-card');
  const hiddenIndices = [];
  
  cards.forEach((card, idx) => {{
    const acom = card.getAttribute('data-acomodacao');
    const colIdx = idx + 2; // offset by 2 for label and vidas columns
    if (type === 'todos' || acom === type) {{
      card.style.display = 'block';
    }} else {{
      card.style.display = 'none';
      hiddenIndices.push(colIdx);
    }}
  }});

  // Filter table columns
  const table = panel.querySelector('table');
  if (!table) return;

  const ths = table.querySelectorAll('thead th');
  const trs = table.querySelectorAll('tbody tr');

  // Update header column visibility
  cards.forEach((card, idx) => {{
    const colIdx = idx + 2;
    if (ths[colIdx]) {{
      if (hiddenIndices.includes(colIdx)) {{
        ths[colIdx].style.display = 'none';
      }} else {{
        ths[colIdx].style.display = '';
      }}
    }}
  }});

  // Update table row cells visibility
  trs.forEach(tr => {{
    if (tr.classList.contains('feature-sep-row')) {{
       const td = tr.querySelector('td');
       if (td) {{
          const visibleCount = cards.length - hiddenIndices.length + 2;
          td.setAttribute('colspan', visibleCount);
       }}
       return;
    }}
    const tds = tr.querySelectorAll('td');
    tds.forEach((td, colIdx) => {{
      if (colIdx >= 2) {{
         if (hiddenIndices.includes(colIdx)) {{
            td.style.display = 'none';
         }} else {{
            td.style.display = '';
         }}
      }}
    }});
  }});

  // Reset selected plan card if it is now hidden
  const selectedSelectedCard = panel.querySelector('.summary-card.selected-plan');
  if (selectedSelectedCard && selectedSelectedCard.style.display === 'none') {{
    selectedSelectedCard.classList.remove('selected-plan');
    const savingsDiv = panel.querySelector('.savings-simulator');
    if (savingsDiv) {{
      savingsDiv.style.display = 'none';
    }}
  }}
}}

function selectPlanCard(insurerSlug, card) {{
  const panel = document.getElementById('panel-' + insurerSlug);
  if (!panel) return;

  // Toggle selected class
  const cards = panel.querySelectorAll('.summary-card');
  cards.forEach(c => c.classList.remove('selected-plan'));
  card.classList.add('selected-plan');

  // Get data attributes
  const planTotal = parseFloat(card.getAttribute('data-plan-total'));
  const planName = card.getAttribute('data-plan-name');
  
  // Calculate savings based on the projected post-readjustment total
  const portoTotal = {fatura_reajuste:.2f};
  const diff = portoTotal - planTotal;
  const annualDiff = diff * 12;

  // Find or create savings container
  let savingsDiv = panel.querySelector('.savings-simulator');
  if (!savingsDiv) {{
    const summaryGrid = panel.querySelector('.summary-grid');
    savingsDiv = document.createElement('div');
    savingsDiv.className = 'savings-simulator fade-in';
    summaryGrid.parentNode.insertBefore(savingsDiv, summaryGrid.nextSibling);
  }}

  // Format values
  const fmt = (val) => {{
    return 'R$ ' + Math.abs(val).toLocaleString('pt-BR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
  }};

  let htmlContent = '';
  if (diff > 0) {{
    // Cheaper plan: Green theme
    htmlContent = `
      <div class="savings-card savings-positive">
        <div class="savings-badge-label">💰 Simulador de Economia</div>
        <div class="savings-grid-layout">
          <div class="savings-column">
            <div class="savings-label">Plano Selecionado</div>
            <div class="savings-value-plan">${{planName}}</div>
          </div>
          <div class="savings-column">
            <div class="savings-label">Economia Mensal</div>
            <div class="savings-value-monthly">${{fmt(diff)}}</div>
          </div>
          <div class="savings-column">
            <div class="savings-label">Economia Anual Estimada</div>
            <div class="savings-value-annual">${{fmt(annualDiff)}}</div>
          </div>
        </div>
        <div class="savings-footer-text">
          ✨ Ao migrar para este cenário, a empresa reduzirá seus custos em <strong>${{fmt(diff)}} por mês</strong>, totalizando uma redução projetada de <strong>${{fmt(annualDiff)}} ao ano (12 meses)</strong>.
        </div>
      </div>
    `;
  }} else if (diff < 0) {{
    // More expensive plan: Amber/Blue theme
    htmlContent = `
      <div class="savings-card savings-negative">
        <div class="savings-badge-label">📊 Comparativo de Custo</div>
        <div class="savings-grid-layout">
          <div class="savings-column">
            <div class="savings-label">Plano Selecionado</div>
            <div class="savings-value-plan">${{planName}}</div>
          </div>
          <div class="savings-column">
            <div class="savings-label">Investimento Adicional / Mês</div>
            <div class="savings-value-monthly" style="color: var(--accent4);">+ ${{fmt(diff)}}</div>
          </div>
          <div class="savings-column">
            <div class="savings-label">Diferença Anual</div>
            <div class="savings-value-annual" style="color: var(--accent4);">+ ${{fmt(annualDiff)}}</div>
          </div>
        </div>
        <div class="savings-footer-text" style="border-top-color: rgba(229,163,54,0.15); color: var(--text-muted);">
          Este plano representa um upgrade de categoria em relação ao Porto Saúde atual, exigindo um aporte mensal adicional de <strong>${{fmt(diff)}}</strong>.
        </div>
      </div>
    `;
  }} else {{
    // Equal
    htmlContent = `
      <div class="savings-card savings-neutral">
        <div class="savings-badge-label">📊 Comparativo de Custo</div>
        <div class="savings-grid-layout">
          <div class="savings-column">
            <div class="savings-label">Plano Selecionado</div>
            <div class="savings-value-plan">${{planName}}</div>
          </div>
          <div class="savings-column" style="grid-column: span 2;">
            <div class="savings-label">Custo Equivalente</div>
            <div class="savings-value-monthly">${{fmt(planTotal)}}</div>
          </div>
        </div>
      </div>
    `;
  }}

  savingsDiv.innerHTML = htmlContent;
  savingsDiv.style.display = 'block';
}}

function showTab(tab) {{
  document.getElementById('tabpanel-vidas').classList.remove('active');
  document.getElementById('tabpanel-unidades').classList.remove('active');
  document.getElementById('tab-vidas').classList.remove('active');
  document.getElementById('tab-unidades').classList.remove('active');

  document.getElementById('tabpanel-' + tab).classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
  currentTab = tab;
}}

function filterEmployees() {{
  const query = document.getElementById('emp-search').value.toLowerCase();
  const rows = document.querySelectorAll('#emp-tbody tr');
  let visible = 0;
  rows.forEach(row => {{
    const text = row.textContent.toLowerCase();
    const show = text.includes(query);
    row.style.display = show ? '' : 'none';
    if (show) visible++;
  }});
  document.getElementById('emp-count').textContent = visible + ' pessoas' + (query ? ' (filtradas)' : '');
}}
</script>

</body>
</html>'''
out_path = os.path.join(base_dir, 'fri_index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML gerado: {out_path}")
print(f"Tamanho: {os.path.getsize(out_path):,} bytes")
