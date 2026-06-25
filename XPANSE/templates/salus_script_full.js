// ───────────────────────────────────────────────

//  RAW DATA  (extracted from XLSX)

// ───────────────────────────────────────────────

let compareList = [];
let currentView = 'normal';
let activeCompany = 'xpanse';
let currentTab = 'vidas';

const COMPANIES = [];
function isComparing(cIdx, sIdx, tIdx, pIdx) {

  return compareList.some(item => item.cIdx === cIdx && item.sIdx === sIdx && item.tIdx === tIdx && item.pIdx === pIdx);

}

function toggleCompare(cIdx, sIdx, tIdx, pIdx) {

  const index = compareList.findIndex(item => item.cIdx === cIdx && item.sIdx === sIdx && item.tIdx === tIdx && item.pIdx === pIdx);

  if (index > -1) {

    compareList.splice(index, 1);

  } else {

    compareList.push({ cIdx, sIdx, tIdx, pIdx });

  }

  

  if (currentView === 'compare') {

    if (compareList.length === 0) toggleCompareView();

    else renderCompareView();

  } else {

    renderMain();

  }

  renderCompareBar();

}

function clearCompare() {

  compareList = [];

  if (currentView === 'compare') toggleCompareView();

  renderMain();

  renderCompareBar();

}

function renderCompareBar() {

  const bar = document.getElementById('compare-bar');

  const count = document.getElementById('compare-count');

  count.innerText = compareList.length;

  if (compareList.length > 0) {

    bar.classList.add('show');

    document.body.classList.add('has-compare');

  } else {

    bar.classList.remove('show');

    document.body.classList.remove('has-compare');

  }

}

function toggleCompareView() {

  const main = document.getElementById('main-layout');

  const compare = document.getElementById('compare-view');

  const btn = document.getElementById('btn-compare-action');

  

  if (currentView === 'main') {

    if (compareList.length === 0) return;

    currentView = 'compare';

    main.style.display = 'none';

    compare.style.display = 'block';

    btn.innerText = 'Voltar';

    renderCompareView();

    window.scrollTo({ top: 0, behavior: 'smooth' });

  } else {

    currentView = 'main';

    main.style.display = 'grid';

    compare.style.display = 'none';

    btn.innerText = 'Ver Comparação';

    renderMain();

    window.scrollTo({ top: 0, behavior: 'smooth' });

  }

}

function renderCompareView() {

  const cv = document.getElementById('compare-view');

  if (compareList.length === 0) return;

  // Find lowest total

  const totals = compareList.map(item => COMPANIES[item.cIdx].sections[item.sIdx].tables[item.tIdx].total ? COMPANIES[item.cIdx].sections[item.sIdx].tables[item.tIdx].total[item.pIdx] : Infinity);

  const minTotal = Math.min(...totals.filter(t => typeof t === 'number'));

  let html = `

    <div style="width:100%">

      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px">

        <h2>Comparativo de Planos</h2>

        <button class="btn-compare-action secondary" style="color: var(--text-main) !important;" onclick="toggleCompareView()">Voltar para Operadoras</button>

      </div>

      <div class="compare-table-wrap fade-in">

        <table class="compare-table">

          <thead>

            <tr>

              <th>Atributos</th>

  `;

  compareList.forEach((item, i) => {

    const c = COMPANIES[item.cIdx];

    const s = c.sections[item.sIdx];

    const t = s.tables[item.tIdx];

    const pName = t.plans[item.pIdx];

    

    html += `

      <th>

        <div class="comp-plan-header">

          ${c.logo ? `<img src="${c.logo}" alt="${c.company}">` : `<div style="font-size:24px">${c.icon||'🏥'}</div>`}

          <h3>${pName}</h3>

          <div class="comp-op">${c.company}</div>

          <button class="remove-compare-btn" style="margin-top:4px" onclick="toggleCompare(${item.cIdx}, ${item.sIdx}, ${item.tIdx}, ${item.pIdx})">Remover</button>

        </div>

      </th>

    `;

  });

  html += `</tr></thead><tbody>`;

  // Total

  html += `<tr><td>Total (${LIVES_DATA.total_vidas} Vidas/mês)</td>`;

  compareList.forEach(item => {

    const t = COMPANIES[item.cIdx].sections[item.sIdx].tables[item.tIdx];

    const val = t.total ? t.total[item.pIdx] : '-';

    const isBest = val === minTotal;

    html += `<td><div class="val-total ${isBest ? 'best-total' : ''}">${val !== '-' ? fmt(val) : '-'}</div>${isBest ? '<div class="best-badge" style="margin-top:4px">★ Menor Preço</div>' : ''}</td>`;

  });

  html += `</tr>`;

  // Modalidade

  html += `<tr><td>Modalidade</td>`;

  compareList.forEach(item => {

    html += `<td><span style="font-size:11px; font-weight:600; color:var(--text-main); background:rgba(0,0,0,0.1); padding:4px 8px; border-radius:4px;">${sectionLabel(COMPANIES[item.cIdx].sections[item.sIdx].name)}</span></td>`;

  });

  html += `</tr>`;

  // Acomodação

  html += `<tr><td>Acomodação</td>`;

  compareList.forEach(item => {

    const acom = COMPANIES[item.cIdx].sections[item.sIdx].tables[item.tIdx].acomodacao?.[item.pIdx] || '-';

    const isApt = acom.toLowerCase().includes('apt');

    html += `<td><span class="${isApt ? 'tag-apt' : 'tag-enf'}" style="font-size:10px; padding:3px 8px">${isApt ? 'APARTAMENTO' : 'ENFERMARIA'}</span></td>`;

  });

  html += `</tr>`;

  // Abrangência

  html += `<tr><td>Abrangência</td>`;

  compareList.forEach(item => html += `<td>${COMPANIES[item.cIdx].sections[item.sIdx].tables[item.tIdx].abrangencia?.[item.pIdx] || '-'}</td>`);

  html += `</tr>`;

  // Reembolso

  html += `<tr><td>Reembolso (Consulta)</td>`;

  compareList.forEach(item => html += `<td>${COMPANIES[item.cIdx].sections[item.sIdx].tables[item.tIdx].reembolso?.[item.pIdx] || '-'}</td>`);

  html += `</tr>`;

  // Redes

  html += `<tr><td>Redes Credenciadas</td>`;

  compareList.forEach(item => {

    const c = COMPANIES[item.cIdx];

    if (c.redes) {

      html += `<td><div style="display:flex; flex-direction:column; gap:6px;">${c.redes.map(r => `<button class="btn-outline" style="border-color:var(--accent); color:var(--accent); font-size:11px; padding:4px" onclick="window.open('${r.file}', '_blank')">🏥 ${r.label}</button>`).join('')}</div></td>`;

    } else {

      html += `<td>-</td>`;

    }

  });

  html += `</tr>`;

  // Age Ranges

  html += `<tr><td colspan="${compareList.length + 1}" class="compare-section-title">Preços por Faixa Etária</td></tr>`;

  

  const ageLabels = ["0 a 18", "19 a 23", "24 a 28", "29 a 33", "34 a 38", "39 a 43", "44 a 48", "49 a 53", "54 a 58", "59 ou mais"];

  

  ageLabels.forEach((label) => {

    const livesCount = LIVES_DATA.faixas[label] || 0;
    html += `<tr><td>${label} <span style="color:var(--text-muted); font-size:11px; font-weight:normal;">(${livesCount} vida${livesCount > 1 ? 's' : ''})</span></td>`;

    const vals = compareList.map(item => {

      const ad = COMPANIES[item.cIdx].sections[item.sIdx].tables[item.tIdx].age_data;

      const row = ad.find(r => r.label === label);

      return row ? row.values[item.pIdx] : Infinity;

    });

    const minAge = Math.min(...vals.filter(v => typeof v === 'number'));

    compareList.forEach((item, i) => {

      const v = vals[i];

      const isBest = v === minAge;

      html += `<td style="color:var(--text-main); font-weight:${isBest ? '700':'400'}; ${isBest ? 'color:var(--accent3)' : ''}">${v !== Infinity ? fmt(v) : '-'}</td>`;

    });

    html += `</tr>`;

  });

  // Diferenciais

  html += `<tr><td colspan="${compareList.length + 1}" class="compare-section-title">Diferenciais e Regras</td></tr>`;

  html += `<tr><td>Detalhes</td>`;

  compareList.forEach(item => {

    const c = COMPANIES[item.cIdx];

    if (c.diferenciais) {

      html += `<td><ul class="diferenciais-list" style="padding-left:0; gap:6px; font-size:12px;">

        ${c.diferenciais.map(d => `<li>${d}</li>`).join('')}

      </ul></td>`;

    } else {

      html += `<td>-</td>`;

    }

  });

  html += `</tr>`;

  html += `

          </tbody>

        </table>

      </div>

    </div>

  `;

  cv.innerHTML = html;

}

// ───────────────────────────────────────────────

//  HELPERS

// ───────────────────────────────────────────────

function fmt(v) {

  if (typeof v === 'number') {

    return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  }

  return v;

}

function sectionIcon(name) {

  const n = name.toUpperCase();

  if (n.includes('SEM COPAR')) return { cls: 'icon-sem', emoji: '✅' };

  if (n.includes('PARCIAL'))   return { cls: 'icon-par', emoji: '⚡' };

  if (n.includes('30%') || n.includes('TOTAL')) return { cls: 'icon-cop', emoji: '💰' };

  return { cls: 'icon-par', emoji: '📋' };

}

function sectionLabel(name) {

  const n = name.toUpperCase();

  if (n.includes('SEM COPAR')) return 'Sem Coparticipação';

  if (n.includes('PARCIAL'))   return 'Coparticipação Parcial';

  if (n.includes('30%'))       return 'Coparticipação 30%';

  if (n.includes('TOTAL'))     return 'Coparticipação Total 30%';

  if (n.includes('LINHA'))     return name;

  return name;

}

function planCountForCompany(c) {

  let count = 0;

  c.sections.forEach(s => s.tables.forEach(t => { count += t.plans.length; }));

  return count;

}

// ───────────────────────────────────────────────

//  RENDER SIDEBAR

// ───────────────────────────────────────────────

function renderSidebar() {
  const sb = document.getElementById('sidebar');
  if (sb) {
    sb.innerHTML = '<div class="sidebar-label">Operadoras</div>';
  }

  const mobileSelectorWrap = document.getElementById('mobile-selector-wrap');
  let activeCompanyData = activeCompany === 'xpanse' ? { company: 'XPANSE', logo: 'logo-xpanse.png' } : (COMPANIES[activeCompany] || COMPANIES[0]);

  // Render trigger button for mobile
  let mobileHtml = `
    <button class="mobile-select-trigger" onclick="toggleMobileDropdown(event)">
      <div class="mobile-select-trigger-left">
        ${activeCompanyData.logo ? `<img src="${activeCompanyData.logo}">` : `<div class="cb-icon">${activeCompanyData.icon || '🏥'}</div>`}
        <span class="mobile-select-trigger-title">${activeCompanyData.company}</span>
      </div>
      <div class="mobile-select-trigger-arrow">▼</div>
    </button>
    <div class="mobile-select-dropdown">
  `;

  // Render XPANSE button in sidebar desktop
  if (sb) {
    const btn = document.createElement('button');
    btn.className = 'company-btn' + (activeCompany === 'xpanse' ? ' active' : '');
    btn.id = 'company-btn-xpanse';
    btn.innerHTML = `
      <img src="logo-xpanse.png" class="cb-logo" style="width:28px; height:28px; object-fit:contain;">
      <span class="cb-name" style="font-weight: 700;">XPANSE</span>
      <span class="company-count" style="background: var(--accent); color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">Empresa</span>
    `;
    btn.addEventListener('click', () => selectCompany('xpanse'));
    sb.appendChild(btn);

    // Divider
    const div = document.createElement('div');
    div.style.margin = '10px 0';
    div.style.borderTop = '1px solid var(--border)';
    sb.appendChild(div);
  }

  // Render XPANSE option in sidebar mobile
  mobileHtml += `
    <button class="mobile-select-option${activeCompany === 'xpanse' ? ' active' : ''}" onclick="selectMobileCompany('xpanse', event)">
      <div class="mobile-select-trigger-left">
        <img src="logo-xpanse.png" style="width:28px; height:28px; object-fit:contain; border:1px solid var(--border); border-radius:4px; padding:2px; background:#fff;">
        <span class="mobile-select-trigger-title" style="font-weight: 700;">XPANSE</span>
      </div>
      <span class="company-count" style="background: var(--accent); color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">Empresa</span>
    </button>
    <div style="border-top: 1px solid var(--border); margin: 4px 0;"></div>
  `;

  COMPANIES.forEach((c, i) => {
    if (sb) {
      const btn = document.createElement('button');
      btn.className = 'company-btn' + (activeCompany === i ? ' active' : '');
      btn.id = `company-btn-${i}`;
      btn.innerHTML = `
        ${c.logo ? `<img src="${c.logo}" class="cb-logo">` : `<div class="cb-icon">${c.icon || '🏥'}</div>`}
        <span class="cb-name">${c.company}</span>
        <span class="company-count">${c.sections.length} seções</span>
      `;
      btn.addEventListener('click', () => selectCompany(i));
      sb.appendChild(btn);
    }

    // Mobile option HTML accumulation
    mobileHtml += `
      <button class="mobile-select-option${activeCompany === i ? ' active' : ''}" onclick="selectMobileCompany(${i}, event)">
        <div class="mobile-select-trigger-left">
          ${c.logo ? `<img src="${c.logo}" style="width:28px; height:28px; object-fit:contain; border:1px solid var(--border); border-radius:4px; padding:2px; background:#fff;">` : `<div class="cb-icon" style="width:28px; height:28px; font-size:12px; display:flex; align-items:center; justify-content:center; border:1px solid var(--border); border-radius:4px;">${c.icon || '🏥'}</div>`}
          <span class="mobile-select-trigger-title">${c.company}</span>
        </div>
        <span class="company-count">${c.sections.length} seções</span>
      </button>
    `;
  });

  mobileHtml += `</div>`;
  if (mobileSelectorWrap) {
    mobileSelectorWrap.innerHTML = mobileHtml;
  }
}

function toggleMobileDropdown(event) {
  event.stopPropagation();
  const wrap = document.getElementById('mobile-selector-wrap');
  if (wrap) wrap.classList.toggle('open');
}

function selectMobileCompany(idx, event) {
  event.stopPropagation();
  selectCompany(idx);
  const wrap = document.getElementById('mobile-selector-wrap');
  if (wrap) wrap.classList.remove('open');
}

// Close when clicking outside
document.addEventListener('click', () => {
  const wrap = document.getElementById('mobile-selector-wrap');
  if (wrap) wrap.classList.remove('open');
});

// ───────────────────────────────────────────────

//  RENDER MAIN

// ───────────────────────────────────────────────

function selectCompany(idx) {

  activeCompany = idx;

  renderSidebar();

  renderMain();

}

// Filtros globais
let filterCoparticipacao = 'todos'; // 'todos', 'com', 'sem'
let filterAcomodacao = 'todos';     // 'todos', 'apartamento', 'enfermaria'

function setFilterCoparticipacao(val) {
  filterCoparticipacao = val;
  renderMain();
}

function setFilterAcomodacao(val) {
  filterAcomodacao = val;
  renderMain();
}

function renderMain() {
  if (activeCompany === 'xpanse') {
    renderCompanyOverview();
    return;
  }

  const main = document.getElementById('main-content');
  if (activeCompany === null) {
    main.innerHTML = '<div class="empty-state"><div class="big-icon">🏥</div><p>Selecione uma operadora no painel ao lado.</p></div>';
    return;
  }
  const c = COMPANIES[activeCompany];

  // Helper filter function
  const planMatchesFilter = (table, pi) => {
    if (filterAcomodacao === 'todos') return true;
    const acom = table.acomodacao ? table.acomodacao[pi] : '';
    const isApt = acom && acom.toLowerCase().includes('apt');
    if (filterAcomodacao === 'apartamento' && isApt) return true;
    if (filterAcomodacao === 'enfermaria' && !isApt) return true;
    return false;
  };

  // 1. Filtrar dinamicamente e calcular estatísticas com base nos filtros
  let visibleSectionCount = 0;
  let visiblePlanCount = 0;
  const filteredTotals = [];

  c.sections.forEach(section => {
    const isSemCopar = section.name.toUpperCase().includes('SEM COPAR');
    if (filterCoparticipacao === 'com' && isSemCopar) return;
    if (filterCoparticipacao === 'sem' && !isSemCopar) return;

    let hasVisiblePlans = false;
    section.tables.forEach(table => {
      table.plans.forEach((plan, pi) => {
        if (planMatchesFilter(table, pi)) {
          visiblePlanCount++;
          hasVisiblePlans = true;
          if (table.total && typeof table.total[pi] === 'number') {
            filteredTotals.push(table.total[pi]);
          }
        }
      });
    });

    if (hasVisiblePlans) {
      visibleSectionCount++;
    }
  });

  const minTotal = filteredTotals.length ? Math.min(...filteredTotals) : 0;

  // Build HTML
  let html = '';

  // 2. Company header (com estatísticas dinâmicas)
  html += `
  <div class="company-header fade-in">
    <div class="company-header-accent"></div>
    <div class="company-header-content">
      ${c.logo ? `<img src="${c.logo}" class="company-logo-large" alt="${c.company}">` : `<div class="company-logo-circle" style="background:linear-gradient(135deg,${c.color}cc,${c.color}88)">${c.icon || '🏥'}</div>`}
      <div class="company-info">
        <h2>${c.company}</h2>
        <p>
          <span>${visibleSectionCount} modalidade${visibleSectionCount > 1 ? 's' : ''}</span>
          <span class="info-dot"></span>
          <span>${visiblePlanCount} plano${visiblePlanCount > 1 ? 's' : ''}</span>
          <span class="info-dot"></span>
          <span>87 vidas</span>
          <span class="info-dot"></span>
          <span>Nacional</span>
        </p>
        ${c.redes ? `
        <div class="company-rede-btns">
          ${c.redes.map(r => `<a class="btn-rede" href="${r.file}" target="_blank">📋 ${r.label}</a>`).join('')}
        </div>` : ''}
      </div>
      <div class="company-stats">
        <div class="stat-box">
          <div class="sv">${visibleSectionCount}</div>
          <div class="sl">Modalidades</div>
        </div>
        <div class="stat-box">
          <div class="sv">${visiblePlanCount}</div>
          <div class="sl">Planos</div>
        </div>
        <div class="stat-box stat-highlight">
          <div class="sv">${minTotal > 0 ? fmt(minTotal) : '-'}</div>
          <div class="sl">Menor total/mês</div>
        </div>
      </div>
    </div>
  </div>`;

  // 3. Renderizar Barra de Filtros Segmentados
  html += `
  <div class="filter-bar">
    <div class="filter-group">
      <div class="filter-label">Coparticipação</div>
      <div class="filter-buttons">
        <button class="filter-btn ${filterCoparticipacao === 'todos' ? 'active' : ''}" onclick="setFilterCoparticipacao('todos')">Todos</button>
        <button class="filter-btn ${filterCoparticipacao === 'com' ? 'active' : ''}" onclick="setFilterCoparticipacao('com')">Com Copart.</button>
        <button class="filter-btn ${filterCoparticipacao === 'sem' ? 'active' : ''}" onclick="setFilterCoparticipacao('sem')">Sem Copart.</button>
      </div>
    </div>
    
    <div class="filter-group">
      <div class="filter-label">Acomodação</div>
      <div class="filter-buttons">
        <button class="filter-btn ${filterAcomodacao === 'todos' ? 'active' : ''}" onclick="setFilterAcomodacao('todos')">Todos</button>
        <button class="filter-btn ${filterAcomodacao === 'apartamento' ? 'active' : ''}" onclick="setFilterAcomodacao('apartamento')">Apartamento</button>
        <button class="filter-btn ${filterAcomodacao === 'enfermaria' ? 'active' : ''}" onclick="setFilterAcomodacao('enfermaria')">Enfermaria</button>
      </div>
    </div>
  </div>
  `;

  // 4. Renderizar Seções
  html += `<div class="fade-in-delay">`;

  let renderedAnySection = false;

  c.sections.forEach((section, si) => {
    const isSemCopar = section.name.toUpperCase().includes('SEM COPAR');
    if (filterCoparticipacao === 'com' && isSemCopar) return;
    if (filterCoparticipacao === 'sem' && !isSemCopar) return;

    const { cls, emoji } = sectionIcon(section.name);
    let cardCls = '';
    if (cls === 'icon-sem') cardCls = 'sem-copar';
    else if (cls === 'icon-par') cardCls = 'copar-parcial';
    else if (cls === 'icon-cop') cardCls = 'copar-30';

    section.tables.forEach((table, ti) => {
      // Verificar planos visíveis nesta tabela
      const visiblePlansIndices = [];
      table.plans.forEach((plan, pi) => {
        if (planMatchesFilter(table, pi)) {
          visiblePlansIndices.push(pi);
        }
      });

      if (visiblePlansIndices.length === 0) return;

      renderedAnySection = true;

      html += `
      <div class="section-card ${cardCls}">
        <div class="section-header">
          <div class="section-icon ${cls}">${emoji}</div>
          <div>
            <div class="section-title">${sectionLabel(section.name)}</div>
            <div class="section-subtitle">${visiblePlansIndices.length} plano${visiblePlansIndices.length > 1 ? 's' : ''} visível${visiblePlansIndices.length > 1 ? 's' : ''} nesta modalidade</div>
          </div>
        </div>
      `;

      // Renderizar summary cards visíveis
      if (table.total) {
        const tableTotals = visiblePlansIndices.map(pi => table.total[pi]).filter(v => typeof v === 'number');
        const tMin = tableTotals.length ? Math.min(...tableTotals) : Infinity;

        html += `<div class="summary-grid" style="padding:16px 20px">`;
        table.plans.forEach((plan, pi) => {
          if (!planMatchesFilter(table, pi)) return;

          const tot = table.total[pi];
          const isMin = typeof tot === 'number' && tot === tMin;
          const acom = table.acomodacao ? table.acomodacao[pi] : '';
          const isApt = acom && acom.toLowerCase().includes('apt');

          html += `
          <div class="summary-card ${isMin ? 'best-value' : ''}">
            ${isMin ? '<div class="best-badge">★ Menor preço</div>' : ''}
            <div class="plan-name" title="${plan}">${plan}</div>
            <div class="acomodacao-tag">
              ${acom ? `<span class="${isApt ? 'tag-apt' : 'tag-enf'}">${isApt ? 'APART.' : 'ENFER.'}</span>` : ''}
            </div>
            <div class="total-value">${fmt(tot)}</div>
            <div class="total-label">total 87 vidas/mês</div>
            <button class="compare-toggle-btn ${isComparing(activeCompany, si, ti, pi) ? 'active' : ''}" onclick="toggleCompare(${activeCompany}, ${si}, ${ti}, ${pi})">
              ${isComparing(activeCompany, si, ti, pi) ? '✓ Comparando' : '➕ Comparar'}
            </button>
          </div>`;
        });
        html += `</div>`;
      }

      // Renderizar age table
      html += `
      <details class="age-drawer">
        <summary>Visualizar tabela completa de preços por faixa etária</summary>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Faixa Etária</th>
                <th>Vidas</th>`;
      table.plans.forEach((plan, pi) => {
        if (!planMatchesFilter(table, pi)) return;
        const acom = table.acomodacao ? table.acomodacao[pi] : '';
        const isApt = acom && acom.toLowerCase().includes('apt');
        html += `<th class="th-plan ${isApt ? 'th-apt' : 'th-enf'}" title="${plan}">${plan}</th>`;
      });
      html += `
              </tr>
            </thead>
            <tbody>`;

      table.age_data.forEach(row => {
        const visibleVals = visiblePlansIndices.map(pi => row.values[pi]).filter(v => typeof v === 'number');
        const rowMin = visibleVals.length ? Math.min(...visibleVals) : Infinity;

        html += `
              <tr>
                <td>${row.label}</td>
                <td style="text-align: center; font-weight: 600; color: var(--text-muted);">${LIVES_DATA.faixas[row.label.trim()] || 0}</td>`;
        row.values.forEach((v, pi) => {
          if (!planMatchesFilter(table, pi)) return;
          const isBest = typeof v === 'number' && v === rowMin && visibleVals.length > 1;
          html += `<td class="${isBest ? 'cell-best' : 'cell-value'}">${fmt(v)}</td>`;
        });
        html += `
              </tr>`;
      });

      // Total row
      if (table.total) {
        html += `
              <tr class="total-row">
                <td>Total/mês</td>
                <td style="text-align: center; font-weight: 700;">${LIVES_DATA.total_vidas}</td>`;
        table.total.forEach((tot, pi) => {
          if (!planMatchesFilter(table, pi)) return;
          html += `<td>${fmt(tot)}</td>`;
        });
        html += `
              </tr>`;
      }

      html += `
            </tbody>
          </table>
        </div>
      </details>
      `;

      // Diferenciais
      if (table.diferenciais && table.diferenciais.length > 0) {
        html += `
        <div class="diferenciais-box" style="margin: 20px 20px 24px;">
          <div class="diferenciais-title">
            <span style="font-size:16px">📋</span> Diferenciais & Observações
          </div>
          <ul class="diferenciais-list">
            ${table.diferenciais.map(d => `<li>${d}</li>`).join('')}
          </ul>
        </div>`;
      }

      html += `</div>`; // fechar section-card
    });
  });

  if (!renderedAnySection) {
    html += `
    <div class="empty-state" style="padding: 40px 20px;">
      <div class="big-icon">🔍</div>
      <p>Nenhum plano corresponde aos filtros selecionados.</p>
      <button class="btn-compare-action" style="margin-top:12px; font-size:12px; padding:6px 16px" onclick="setFilterCoparticipacao('todos'); setFilterAcomodacao('todos')">Limpar Filtros</button>
    </div>`;
  }

  // Diferenciais no final da aba da operadora
  if (c.diferenciais && c.diferenciais.length > 0) {
    html += `
    <div class="diferenciais-box" style="margin-top: 24px;">
      <div class="diferenciais-title">
        <span style="font-size:16px">ℹ️</span> Regras de Aceitação & Informações Gerais
      </div>
      <ul class="diferenciais-list">
        ${c.diferenciais.map(d => `<li>${d}</li>`).join('')}
      </ul>
    </div>`;
  }

  html += `</div>`; // fechar fade-in-delay

  main.innerHTML = html;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ───────────────────────────────────────────────

//  INIT

// ───────────────────────────────────────────────

renderSidebar();

// Auto-select first company

selectCompany('xpanse');


// ───────────────────────────────────────────────
//  XPANSE COMPANY OVERVIEW & RELAÇÃO DE VIDAS
// ───────────────────────────────────────────────

function showTab(tabName) {
  currentTab = tabName;
  renderMain();
}

function renderCompanyOverview() {
  const main = document.getElementById('main-content');
  if (!main) return;

  let cltCount = LIVES_DATA.regimes.CLT || 0;
  let pjCount = LIVES_DATA.regimes.PJ || 0;
  let totalCount = LIVES_DATA.total_vidas || 87;

  let html = `
  <div class="company-header fade-in" style="background: #ffffff; border: 1px solid var(--border); border-radius: 16px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); position: relative; overflow: hidden;">
    <div class="company-header-accent" style="position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: var(--accent);"></div>
    <div class="company-header-content" style="display: flex; align-items: center; padding: 24px; flex-wrap: wrap; gap: 20px;">
      <img src="logo-xpanse.png" class="company-logo-large" alt="XPANSE" style="max-height: 70px; max-width: 170px; object-fit: contain;">
      <div class="company-info" style="flex-grow: 1;">
        <h2 style="font-size: 24px; font-weight: 800; color: var(--accent2); margin: 0 0 8px 0;">XPANSE</h2>
        <p style="margin: 0; color: var(--text-muted); font-size: 14px; display: flex; align-items: center; gap: 8px;">
          <span>Matriz & Filiais</span>
          <span class="info-dot" style="width: 4px; height: 4px; background: var(--text-muted); border-radius: 50%; display: inline-block;"></span>
          <span>${totalCount} colaboradores</span>
          <span class="info-dot" style="width: 4px; height: 4px; background: var(--text-muted); border-radius: 50%; display: inline-block;"></span>
          <span>Estudo PME</span>
        </p>
      </div>
      <div class="company-stats" style="display: flex; gap: 16px; margin-left: auto;">
        <div class="stat-box" style="text-align: center; padding: 12px 20px; border-radius: 12px; background: var(--bg-card2); border: 1px solid var(--border); min-width: 90px;">
          <div class="sv" style="font-size: 24px; font-weight: 800; color: var(--accent);">${totalCount}</div>
          <div class="sl" style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-top: 4px;">Total Vidas</div>
        </div>
        <div class="stat-box" style="text-align: center; padding: 12px 20px; border-radius: 12px; background: var(--bg-card2); border: 1px solid var(--border); min-width: 90px;">
          <div class="sv" style="font-size: 24px; font-weight: 800; color: var(--accent);">${cltCount}</div>
          <div class="sl" style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-top: 4px;">CLT</div>
        </div>
        <div class="stat-box" style="text-align: center; padding: 12px 20px; border-radius: 12px; background: var(--bg-card2); border: 1px solid var(--border); min-width: 90px;">
          <div class="sv" style="font-size: 24px; font-weight: 800; color: var(--accent);">${pjCount}</div>
          <div class="sl" style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-top: 4px;">PJ</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Tabs Bar -->
  <div class="tabs-bar" style="display: flex; gap: 12px; border-bottom: 2px solid var(--border); margin-bottom: 24px; padding-bottom: 8px;">
    <button class="tab-btn" id="tab-vidas" style="background: none; border: none; padding: 8px 16px; font-weight: 600; font-size: 15px; cursor: pointer; color: ${currentTab === 'vidas' ? 'var(--accent)' : 'var(--text-muted)'}; border-bottom: 3px solid ${currentTab === 'vidas' ? 'var(--accent)' : 'transparent'}; transition: all 0.3s ease;" onclick="showTab('vidas')">👥 Relação de Vidas</button>
    <button class="tab-btn" id="tab-unidades" style="background: none; border: none; padding: 8px 16px; font-weight: 600; font-size: 15px; cursor: pointer; color: ${currentTab === 'unidades' ? 'var(--accent)' : 'var(--text-muted)'}; border-bottom: 3px solid ${currentTab === 'unidades' ? 'var(--accent)' : 'transparent'}; transition: all 0.3s ease;" onclick="showTab('unidades')">🏢 Filiais Consideradas</button>
  </div>

  <!-- Panel Content -->
  <div id="tabpanel-content" class="fade-in">
  `;

  if (currentTab === 'vidas') {
    html += `
    <div class="employees-section" style="background: #ffffff; border: 1px solid var(--border); border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
      <div class="employees-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
        <h3 style="font-size: 18px; font-weight: 700; color: var(--accent2); margin: 0;">👥 Relação de Vidas</h3>
        <div class="employees-search">
          <input type="text" class="search-input" id="emp-search" placeholder="Buscar colaborador..." oninput="filterEmployees()" style="padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; width: 250px; font-size: 14px; outline: none; transition: border-color 0.2s;" onfocus="this.style.borderColor='var(--accent)'" onblur="this.style.borderColor='var(--border)'">
        </div>
      </div>
      <div class="employees-table-wrap" style="max-height: 500px; overflow-y: auto; border: 1px solid var(--border); border-radius: 12px;">
        <table class="employees-table" id="emp-table" style="width: 100%; border-collapse: collapse; font-size: 14px;">
          <thead style="position: sticky; top: 0; background: var(--bg-card2); z-index: 10; box-shadow: 0 1px 0 var(--border);">
            <tr>
              <th style="text-align: left; padding: 12px 16px; font-weight: 600; color: var(--accent2);">Nome</th>
              <th style="text-align: center; padding: 12px 16px; font-weight: 600; color: var(--accent2); width: 120px;">Idade</th>
              <th style="text-align: center; padding: 12px 16px; font-weight: 600; color: var(--accent2); width: 120px;">Regime</th>
            </tr>
          </thead>
          <tbody id="emp-tbody">
          </tbody>
        </table>
      </div>
      <div class="employees-footer" style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; font-size: 14px; font-weight: 600; color: var(--text-muted);">
        <span id="emp-count">${EMPLOYEES.length} colaboradores</span>
      </div>
    </div>
    `;
  } else {
    // tab === 'unidades'
    html += `
    <div class="unidades-section">
      <h3 style="font-size: 18px; font-weight: 700; color: var(--accent2); margin: 0 0 20px 0;">🏢 Filiais & Matriz</h3>
      <div class="unidades-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;">
    `;

    const units = [
      { name: "XPANSE MATRIZ", cnpj: "55.786.243/0001-99", type: "Matriz" },
      { name: "Filial RM", cnpj: "53.073.042/0001-19", type: "Filial" },
      { name: "Filial Campo Limpo", cnpj: "55.786.243/0007-84", type: "Filial" },
      { name: "Filial Carapicuíba", cnpj: "55.786.243/0004-31", type: "Filial" },
      { name: "Filial Grand Plaza", cnpj: "55.786.243/0008-65", type: "Filial" },
      { name: "Filial Mauá", cnpj: "55.786.243/0002-70", type: "Filial" },
      { name: "Filial Metropole", cnpj: "55.786.243/0009-46", type: "Filial" },
      { name: "Filial Raposo", cnpj: "55.786.243/0003-50", type: "Filial" },
      { name: "Filial São Bernardo", cnpj: "55.786.243/0005-12", type: "Filial" },
      { name: "Filial Mogi", cnpj: "55.786.243/0014-03", type: "Filial" },
      { name: "Filial Suzano", cnpj: "55.786.243/0013-22", type: "Filial" },
      { name: "Filial Itaquera", cnpj: "55.786.243/0015-94", type: "Filial" },
      { name: "Filial Center Norte", cnpj: "55.786.243.0016-75", type: "Filial" }
    ];

    units.forEach(u => {
      html += `
      <div class="unidade-card fade-in" style="background:#ffffff; border: 1px solid var(--border); border-radius: 12px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; align-items: flex-start; gap: 16px; transition: transform 0.2s, box-shadow 0.2s;" onmouseenter="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.05)';" onmouseleave="this.style.transform='none'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.02)';">
        <div class="unidade-icon" style="width: 44px; height: 44px; border-radius: 8px; background: ${u.type === 'Matriz' ? 'rgba(48,86,156,0.1)' : 'rgba(46,203,150,0.1)'}; color: ${u.type === 'Matriz' ? 'var(--accent)' : 'var(--accent3)'}; display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0;">
          ${u.type === 'Matriz' ? '👑' : '🏢'}
        </div>
        <div style="flex-grow: 1;">
          <div class="unidade-name" style="font-weight: 700; color: var(--accent2); font-size: 15px;">${u.name}</div>
          <div class="unidade-sub" style="font-size: 12px; color: var(--text-muted); margin-top: 4px; font-family: monospace; word-break: break-all;">CNPJ: ${u.cnpj}</div>
          <span style="display: inline-block; font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; margin-top: 8px; background: ${u.type === 'Matriz' ? 'rgba(48,86,156,0.1)' : 'rgba(46,203,150,0.1)'}; color: ${u.type === 'Matriz' ? 'var(--accent)' : 'var(--accent3)'};">
            ${u.type}
          </span>
        </div>
      </div>
      `;
    });

    html += `
      </div>
    </div>
    `;
  }

  html += `
  </div> <!-- close tabpanel-content -->
  `;

  main.innerHTML = html;

  if (currentTab === 'vidas') {
    fillEmployeesTable();
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function fillEmployeesTable() {
  const tbody = document.getElementById('emp-tbody');
  if (!tbody) return;

  let html = '';
  EMPLOYEES.forEach(emp => {
    const badgeClass = emp.regime === 'PJ' ? 'badge-dep' : 'badge-titular';
    const badgeLabel = emp.regime;
    
    html += `
    <tr style="border-bottom: 1px solid var(--border); transition: background-color 0.1s;" onmouseenter="this.style.backgroundColor='var(--bg-card2)'" onmouseleave="this.style.backgroundColor='transparent'">
      <td style="padding: 12px 16px; font-weight: 500; color: var(--text-main);">${emp.name}</td>
      <td style="padding: 12px 16px; text-align: center; color: var(--text-main); font-weight: 600;">${emp.age} anos</td>
      <td style="padding: 12px 16px; text-align: center;">
        <span class="person-badge ${badgeClass}" style="padding: 4px 8px; font-size: 11px; font-weight: 700; border-radius: 4px; display: inline-block; min-width: 40px; text-align: center;">
          ${badgeLabel}
        </span>
      </td>
    </tr>
    `;
  });
  tbody.innerHTML = html;
}

function filterEmployees() {
  const query = document.getElementById('emp-search').value.toLowerCase();
  const rows = document.querySelectorAll('#emp-table tbody tr');
  let count = 0;

  rows.forEach(row => {
    const name = row.cells[0].textContent.toLowerCase();
    if (name.includes(query)) {
      row.style.display = '';
      count++;
    } else {
      row.style.display = 'none';
    }
  });

  const counter = document.getElementById('emp-count');
  if (counter) {
    counter.textContent = `${count} colaboradores encontrados`;
  }
}