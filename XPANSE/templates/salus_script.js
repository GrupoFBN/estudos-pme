

// ───────────────────────────────────────────────

//  RAW DATA  (extracted from XLSX)

// ───────────────────────────────────────────────

const COMPANIES = [];

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
          <span>66 vidas</span>
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
            <div class="total-label">total 66 vidas/mês</div>
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
                <th>Faixa Etária</th>`;
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
                <td>${row.label}</td>`;
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
                <td>Total 66 Vidas/mês</td>`;
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

  html += `</div>`; // fechar fade-in-delay

  main.innerHTML = html;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ───────────────────────────────────────────────

//  INIT

// ───────────────────────────────────────────────

renderSidebar();

// Auto-select first company

selectCompany(0);

