// MACLOVIN NEWS — Full-Featured Editorial Controller

let cachedBriefings = {};
let currentData = {
  tools: [],
  opportunities: [],
  business: [],
  news: [],
  learning: [],
  geek: [],
};

let activeTab = 'tools';
let activeSubfilter = 'all';
let activePricing = 'all';
let activeSource = 'all';
let activeSort = 'recent'; // 'recent', 'relevance', 'az'
let currentLayout = 'grid'; // 'grid' | 'list'
let searchQuery = '';

// DOM Elements
const dateSelect = document.getElementById('dateSelect');
const btnSync = document.getElementById('btnSync');
const searchInput = document.getElementById('searchInput');
const clearSearch = document.getElementById('clearSearch');
const sourceFilter = document.getElementById('sourceFilter');
const sortSelect = document.getElementById('sortSelect');
const btnLayoutGrid = document.getElementById('btnLayoutGrid');
const btnLayoutList = document.getElementById('btnLayoutList');
const contextualFiltersRow = document.getElementById('contextualFiltersRow');
const cardsGrid = document.getElementById('cardsGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const footerStats = document.getElementById('footerStats');
const currentDateDisplay = document.getElementById('currentDateDisplay');
const dbIndicator = document.getElementById('dbIndicator');

// Export Buttons
const btnCopySummary = document.getElementById('btnCopySummary');
const btnDownloadMd = document.getElementById('btnDownloadMd');
const btnDownloadJson = document.getElementById('btnDownloadJson');

// Modal Elements
const detailModal = document.getElementById('detailModal');
const modalBackdrop = document.getElementById('modalBackdrop');
const modalClose = document.getElementById('modalClose');
const modalBody = document.getElementById('modalBody');
const toastNotification = document.getElementById('toastNotification');

// Counter Badges
const badgeTools = document.getElementById('badgeTools');
const badgeOpportunities = document.getElementById('badgeOpportunities');
const badgeBusiness = document.getElementById('badgeBusiness');
const badgeNews = document.getElementById('badgeNews');
const badgeLearning = document.getElementById('badgeLearning');
const badgeGeek = document.getElementById('badgeGeek');

// Semantic keywords for strict client-side category separation
const GEEK_KW = [
  'game', 'jogos', 'jogo', 'gameplay', 'gamer', 'playstation', 'ps5', 'ps4', 'xbox', 'nintendo', 'switch',
  'steam', 'gta', 'rpg', 'filme', 'filmes', 'cinema', 'movie', 'série', 'series', 'trailer', 'teaser',
  'hq', 'hqs', 'quadrinho', 'quadrinhos', 'comic', 'comics', 'mangá', 'manga', 'anime', 'animes',
  'marvel', 'dc', 'batman', 'superman', 'vingadores', 'star wars', 'geek', 'nerd', 'cosplay',
  'rtx', 'geforce', 'radeon', 'gpu gamer', 'steam deck', 'alienware'
];

const LEARNING_KW = [
  'tutorial', 'como criar', 'como construir', 'how to', 'guide', 'guia', 'passo a passo', 'step by step',
  'arquitetura', 'architecture', 'deep dive', 'deep-dive', 'paper', 'whitepaper', 'benchmark',
  'como funciona', 'how it works', 'best practices', 'boas práticas', 'roadmap', 'cheatsheet', 'handbook',
  'system design', 'engenharia de software', 'aprenda', 'curso'
];

const OPPORTUNITY_KW = [
  'oportunidade', 'opportunity', 'monetizar', 'monetization', 'como lucrar', 'vender', 'venda', 'ideia de negócio',
  'business idea', 'micro-saas', 'micro saas', 'side project', 'indie hacker', 'white-label', 'white label',
  'automação empresarial', 'solução para empresas', 'reduzir custos', 'para sua empresa', 'aplicar no negócio',
  'mvp', 'boilerplate', 'template comercial', 'b2b', 'para clientes', 'case de sucesso', 'solução comercial',
  'como implementar na empresa', 'transforme em produto'
];

const BUSINESS_KW = [
  'funding', 'valuation', 'venture capital', 'vc', 'round', 'rodada', 'investimento', 'investors', 'investidores',
  'm&a', 'acquisition', 'acquire', 'adquire', 'aquisição', 'comprar', 'comprou', 'startup', 'startups',
  'ipo', 'lucro', 'receita', 'faturamento', 'revenue', 'quarter', 'trimestre', 'ações', 'shares', 'stock',
  'wall street', 'demissão', 'demissões', 'layoff', 'layoffs', 'aporte', 'aportou', 'série a', 'série b',
  'seed', 'pre-seed', 'unicórnio', 'unicorn', 'fintech', 'market cap', 'captação', 'fundraise'
];

const TOOL_KW = [
  'tool', 'ferramenta', 'software', 'open-source', 'open source', 'código aberto', 'github', 'repositório',
  'repository', 'library', 'biblioteca', 'framework', 'saas', 'extension', 'extensão', 'plugin', 'sdk', 'api',
  'npm', 'pypi', 'docker', 'qwen', 'llama', 'whisper', 'claude code', 'cursor', 'ollama', 'vllm', 'langchain', 'show hn'
];

function classifyItemStrict(item) {
  const text = `${item.title || ''} ${item.summary || ''} ${item.canonical_url || ''} ${item.source_id || ''}`.toLowerCase();
  
  for (const kw of GEEK_KW) {
    if (text.includes(kw)) return 'geek';
  }
  for (const kw of OPPORTUNITY_KW) {
    if (text.includes(kw)) return 'opportunities';
  }
  for (const kw of LEARNING_KW) {
    if (text.includes(kw)) return 'learning';
  }
  for (const kw of BUSINESS_KW) {
    if (text.includes(kw)) return 'business';
  }
  for (const kw of TOOL_KW) {
    if (text.includes(kw)) return 'tools';
  }
  
  if (item.item_type === 'tool' && !GEEK_KW.some(k => text.includes(k))) return 'tools';
  if (item.item_type === 'opportunities') return 'opportunities';
  if (item.item_type === 'business') return 'business';
  if (item.item_type === 'learning') return 'learning';
  if (item.item_type === 'geek') return 'geek';

  return 'news';
}

function detectToolSubtype(item) {
  if (item.tool_subtype === 'repo' || item.tool_subtype === 'app') {
    return item.tool_subtype;
  }
  const text = `${item.title || ''} ${item.summary || ''} ${item.canonical_url || ''}`.toLowerCase();
  if (text.includes('github.com') || text.includes('gitlab.com') || text.includes('huggingface.co') || text.includes('repositório') || text.includes('repository') || text.includes('código aberto') || text.includes('open-source') || text.includes('open source')) {
    return 'repo';
  }
  return 'app';
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  renderContextualFilters();
  await loadHistoryDates();
  await checkDatabaseHealth();
  await fetchBriefing();
});

async function checkDatabaseHealth() {
  try {
    const res = await fetch('/api/status');
    if (res.ok) {
      const data = await res.json();
      if (dbIndicator) {
        dbIndicator.innerHTML = `<span class="db-dot" style="background:#10B981"></span> ${data.database || 'Supabase PostgreSQL'} Conectado`;
      }
    }
  } catch (e) {
    if (dbIndicator) {
      dbIndicator.innerHTML = `<span class="db-dot" style="background:#F59E0B"></span> Modo Local / Fallback`;
    }
  }
}

function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeTab = btn.dataset.tab;
      activeSubfilter = 'all';
      activePricing = 'all';
      
      renderContextualFilters();
      renderCards();
    });
  });

  // Source Filter
  if (sourceFilter) {
    sourceFilter.addEventListener('change', (e) => {
      activeSource = e.target.value;
      renderCards();
    });
  }

  // Sort Filter
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      activeSort = e.target.value;
      renderCards();
    });
  }

  // Layout Toggle
  if (btnLayoutGrid && btnLayoutList) {
    btnLayoutGrid.addEventListener('click', () => {
      btnLayoutGrid.classList.add('active');
      btnLayoutList.classList.remove('active');
      currentLayout = 'grid';
      cardsGrid.className = 'editorial-grid';
    });

    btnLayoutList.addEventListener('click', () => {
      btnLayoutList.classList.add('active');
      btnLayoutGrid.classList.remove('active');
      currentLayout = 'list';
      cardsGrid.className = 'editorial-list';
    });
  }

  // Search Input
  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value.toLowerCase().trim();
    if (searchQuery) {
      clearSearch.classList.remove('hidden');
    } else {
      clearSearch.classList.add('hidden');
    }
    renderCards();
  });

  clearSearch.addEventListener('click', () => {
    searchInput.value = '';
    searchQuery = '';
    clearSearch.classList.add('hidden');
    renderCards();
  });

  // Date Change: Carrega qualquer dia anterior selecionado
  dateSelect.addEventListener('change', () => {
    fetchBriefing(dateSelect.value);
  });

  // Sync Button
  btnSync.addEventListener('click', async () => {
    btnSync.disabled = true;
    btnSync.innerHTML = `<span class="editorial-spinner" style="width:14px;height:14px;border-width:2px;display:inline-block;margin:0"></span> <span class="sync-text">Sincronizando...</span>`;
    
    try {
      const res = await fetch('/api/run', { method: 'POST' });
      if (res.ok) {
        const payload = await res.json();
        showToast('⚡ Base de notícias sincronizada com sucesso!');
        await loadHistoryDates();
        await fetchBriefing();
      } else {
        await fetchBriefing();
      }
    } catch (err) {
      console.warn('Fallback na sincronização:', err);
      await fetchBriefing();
    } finally {
      btnSync.disabled = false;
      btnSync.innerHTML = `<span class="sync-icon">⚡</span> <span class="sync-text">Sincronizar Fontes</span>`;
    }
  });

  // Export Buttons
  if (btnCopySummary) {
    btnCopySummary.addEventListener('click', copyExecutiveSummary);
  }
  if (btnDownloadMd) {
    btnDownloadMd.addEventListener('click', downloadMarkdownReport);
  }
  if (btnDownloadJson) {
    btnDownloadJson.addEventListener('click', downloadJsonData);
  }

  // Modal Close
  if (modalClose) {
    modalClose.addEventListener('click', () => detailModal.classList.add('hidden'));
  }
  if (modalBackdrop) {
    modalBackdrop.addEventListener('click', () => detailModal.classList.add('hidden'));
  }
}

function showToast(message) {
  if (!toastNotification) return;
  toastNotification.textContent = message;
  toastNotification.classList.remove('hidden');
  setTimeout(() => {
    toastNotification.classList.add('hidden');
  }, 3500);
}

function renderContextualFilters() {
  if (!contextualFiltersRow) return;
  contextualFiltersRow.innerHTML = '';

  if (activeTab === 'tools') {
    contextualFiltersRow.innerHTML = `
      <div class="filter-group">
        <span class="filter-label">Tipo:</span>
        <button class="filter-tag active" data-sub="all">Todas as Ferramentas</button>
        <button class="filter-tag" data-sub="repo">📦 Repositórios GitHub</button>
        <button class="filter-tag" data-sub="app">🚀 Aplicativos & SaaS</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">Preço:</span>
        <button class="filter-tag active" data-pricing="all">Todos</button>
        <button class="filter-tag" data-pricing="free">🟢 Grátis / Open Source</button>
        <button class="filter-tag" data-pricing="freemium">🟡 Freemium</button>
        <button class="filter-tag" data-pricing="paid">🔵 Pago / Comercial</button>
      </div>
    `;
  } else if (activeTab === 'opportunities') {
    contextualFiltersRow.innerHTML = `
      <div class="filter-group">
        <span class="filter-label">Foco:</span>
        <button class="filter-tag active" data-sub="all">Todas as Oportunidades</button>
        <button class="filter-tag" data-sub="enterprise">🏢 Soluções Empresariais & Automação</button>
        <button class="filter-tag" data-sub="microsaas">💡 Ideias de Micro-SaaS & B2B</button>
      </div>
    `;
  } else if (activeTab === 'business') {
    contextualFiltersRow.innerHTML = `
      <div class="filter-group">
        <span class="filter-label">Segmento:</span>
        <button class="filter-tag active" data-sub="all">Todos os Negócios</button>
        <button class="filter-tag" data-sub="funding">💰 Rodadas, Aportes & VC</button>
        <button class="filter-tag" data-sub="ma">🤝 Fusões & Aquisições (M&A)</button>
        <button class="filter-tag" data-sub="market">📈 Big Techs & Mercado</button>
      </div>
    `;
  } else if (activeTab === 'news') {
    contextualFiltersRow.innerHTML = `
      <div class="filter-group">
        <span class="filter-label">Categoria:</span>
        <button class="filter-tag active" data-sub="all">Todas as Notícias</button>
        <button class="filter-tag" data-sub="models">🤖 Modelos & LLMs</button>
        <button class="filter-tag" data-sub="regulation">⚖️ Regulação & Governo</button>
      </div>
    `;
  } else if (activeTab === 'learning') {
    contextualFiltersRow.innerHTML = `
      <div class="filter-group">
        <span class="filter-label">Conteúdo:</span>
        <button class="filter-tag active" data-sub="all">Todos os Conteúdos</button>
        <button class="filter-tag" data-sub="tutorials">🛠️ Tutoriais & Guias</button>
        <button class="filter-tag" data-sub="architecture">🏛️ Arquitetura & Engenharia</button>
      </div>
    `;
  } else if (activeTab === 'geek') {
    contextualFiltersRow.innerHTML = `
      <div class="filter-group">
        <span class="filter-label">Universo:</span>
        <button class="filter-tag active" data-sub="all">Toda a Cultura Geek</button>
        <button class="filter-tag" data-sub="games">🎮 Games & Consoles</button>
        <button class="filter-tag" data-sub="movies">🎬 Cinema & Séries</button>
        <button class="filter-tag" data-sub="comics">📚 HQs & Mangás</button>
      </div>
    `;
  }

  // Bind clicks in newly rendered filter tags
  contextualFiltersRow.querySelectorAll('.filter-tag[data-sub]').forEach(tag => {
    tag.addEventListener('click', () => {
      contextualFiltersRow.querySelectorAll('.filter-tag[data-sub]').forEach(t => t.classList.remove('active'));
      tag.classList.add('active');
      activeSubfilter = tag.dataset.sub;
      renderCards();
    });
  });

  contextualFiltersRow.querySelectorAll('.filter-tag[data-pricing]').forEach(tag => {
    tag.addEventListener('click', () => {
      contextualFiltersRow.querySelectorAll('.filter-tag[data-pricing]').forEach(t => t.classList.remove('active'));
      tag.classList.add('active');
      activePricing = tag.dataset.pricing;
      renderCards();
    });
  });
}

function applyData(data) {
  const allItems = [
    ...(data.tools || []),
    ...(data.opportunities || []),
    ...(data.business || []),
    ...(data.news || []),
    ...(data.learning || []),
    ...(data.geek || []),
  ];

  const tools = [];
  const opportunities = [];
  const business = [];
  const news = [];
  const learning = [];
  const geek = [];

  const uniqueSources = new Set();

  allItems.forEach(it => {
    const cat = classifyItemStrict(it);
    it.item_type = cat === 'tools' ? 'tool' : cat;
    it.tool_subtype = detectToolSubtype(it);
    if (it.source_id) uniqueSources.add(it.source_id);
    
    if (cat === 'tools') tools.push(it);
    else if (cat === 'opportunities') opportunities.push(it);
    else if (cat === 'business') business.push(it);
    else if (cat === 'learning') learning.push(it);
    else if (cat === 'geek') geek.push(it);
    else news.push(it);
  });

  currentData.tools = tools;
  currentData.opportunities = opportunities;
  currentData.business = business;
  currentData.news = news;
  currentData.learning = learning;
  currentData.geek = geek;

  // Atualizar badges dos contadores
  if (badgeTools) badgeTools.textContent = currentData.tools.length;
  if (badgeOpportunities) badgeOpportunities.textContent = currentData.opportunities.length;
  if (badgeBusiness) badgeBusiness.textContent = currentData.business.length;
  if (badgeNews) badgeNews.textContent = currentData.news.length;
  if (badgeLearning) badgeLearning.textContent = currentData.learning.length;
  if (badgeGeek) badgeGeek.textContent = currentData.geek.length;

  // Atualizar dropdown de fontes
  if (sourceFilter) {
    const prevSelected = sourceFilter.value;
    sourceFilter.innerHTML = '<option value="all">Todas as Fontes</option>';
    Array.from(uniqueSources).sort().forEach(src => {
      const opt = document.createElement('option');
      opt.value = src;
      opt.textContent = src;
      sourceFilter.appendChild(opt);
    });
    if (uniqueSources.has(prevSelected)) {
      sourceFilter.value = prevSelected;
    }
  }

  // Formatar data de exibição da edição
  if (data.date) {
    try {
      const parts = data.date.split('-');
      if (parts.length === 3) {
        const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        const formatted = d.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
        currentDateDisplay.textContent = `Edição de ${formatted.charAt(0).toUpperCase() + formatted.slice(1)}`;
      }
    } catch (e) {
      currentDateDisplay.textContent = `Edição: ${data.date}`;
    }
  }

  // Atualizar footer
  footerStats.innerHTML = `📅 <strong>Data:</strong> ${data.date} &bull; 📊 <strong>Total de Matérias:</strong> ${allItems.length} &bull; 🗄️ <strong>Banco:</strong> <span style="color:#10B981">Supabase Cloud Ativo</span>`;

  renderCards();
}

async function loadHistoryDates() {
  try {
    let res = await fetch('/api/history');
    if (!res.ok) {
      res = await fetch('/data/history.json');
    }
    const data = await res.json();
    dateSelect.innerHTML = '';
    
    if (data.dates && data.dates.length > 0) {
      data.dates.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = `Edição ${d}`;
        dateSelect.appendChild(opt);
      });
    } else {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'Edição Mais Recente';
      dateSelect.appendChild(opt);
    }
  } catch (err) {
    console.error('Erro ao carregar histórico:', err);
  }
}

async function fetchBriefing(date = '') {
  cardsGrid.innerHTML = '';
  loadingState.classList.remove('hidden');
  emptyState.classList.add('hidden');

  if (date && cachedBriefings[date]) {
    applyData(cachedBriefings[date]);
    loadingState.classList.add('hidden');
    return;
  }

  try {
    let url = date ? `/api/briefing?date=${date}` : '/api/briefing';
    let res = await fetch(url);
    if (!res.ok) {
      const dateUrl = date ? `/data/briefings/${date}.json` : '/data/briefing.json';
      res = await fetch(dateUrl);
      if (!res.ok) {
        res = await fetch('/data/briefing.json');
      }
    }
    const data = await res.json();
    if (data.date) {
      cachedBriefings[data.date] = data;
    }
    applyData(data);
  } catch (err) {
    console.error('Erro ao carregar briefing do dia:', err);
  } finally {
    loadingState.classList.add('hidden');
  }
}

function getSubtypeBadge(subtype) {
  if (subtype === 'repo') {
    return `<span class="subtype-badge badge-repo">📦 Repositório GitHub</span>`;
  }
  return `<span class="subtype-badge badge-app">🚀 App / SaaS</span>`;
}

function getPricingBadge(pricing) {
  const p = (pricing || '').toLowerCase();
  if (p.includes('grátis') || p.includes('open-source') || p.includes('free')) {
    return `<span class="pricing-badge badge-free">🟢 Grátis / Open Source</span>`;
  }
  if (p.includes('freemium')) {
    return `<span class="pricing-badge badge-freemium">🟡 Freemium</span>`;
  }
  if (p.includes('pago') || p.includes('paid') || p.includes('comercial')) {
    return `<span class="pricing-badge badge-paid">🔵 Pago / Comercial</span>`;
  }
  return '';
}

function openModalWithItem(item) {
  if (!detailModal || !modalBody) return;

  const takeawayLabel = activeTab === 'opportunities' 
    ? '💰 Como Lucrar ou Aplicar na Empresa:' 
    : (activeTab === 'business' ? '📈 Análise de Mercado:' : '💡 Contexto & Impacto:');

  modalBody.innerHTML = `
    <div class="card-top" style="margin-bottom:1rem">
      <div class="card-badges-left">
        <span class="card-source-pill">${item.source_id || 'Fonte'}</span>
        ${activeTab === 'tools' ? getSubtypeBadge(item.tool_subtype) : ''}
      </div>
      ${(activeTab === 'tools' || item.pricing_model) ? getPricingBadge(item.pricing_model) : ''}
    </div>
    <h2 style="font-size:1.4rem;font-weight:700;color:var(--text-headline);margin-bottom:1rem;line-height:1.4">${item.title}</h2>
    <p style="font-size:1rem;color:var(--text-primary);line-height:1.6;margin-bottom:1.25rem">${item.summary || item.title}</p>
    ${item.why_it_matters ? `
      <div class="card-takeaway" style="margin-bottom:1.25rem;padding:1rem">
        <strong>${takeawayLabel}</strong> ${item.why_it_matters}
      </div>
    ` : ''}
    ${item.key_features && item.key_features.length > 0 ? `
      <div style="margin-bottom:1.5rem">
        <strong style="color:var(--text-gold);font-size:0.85rem;text-transform:uppercase;display:block;margin-bottom:0.5rem">Destaques & Recursos:</strong>
        <div class="card-tags">
          ${item.key_features.map(f => `<span class="feature-pill" style="font-size:0.85rem;padding:4px 10px">✔ ${f}</span>`).join('')}
        </div>
      </div>
    ` : ''}
    <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--border-subtle);padding-top:1rem;margin-top:1rem">
      <a href="${item.canonical_url || '#'}" target="_blank" rel="noopener noreferrer" class="btn-primary-action" style="padding:0.6rem 1.5rem">
        Acessar Link Original ↗
      </a>
      <span class="card-pubtime">${item.published_date_utc || 'Data de Hoje'}</span>
    </div>
  `;

  detailModal.classList.remove('hidden');
}

function copyExecutiveSummary() {
  const dateStr = dateSelect.value || new Date().toISOString().split('T')[0];
  let text = `⚡ MACLOVIN NEWS — RESUMO EXECUTIVO (${dateStr})\n`;
  text += `============================================================\n\n`;

  if (currentData.tools.length > 0) {
    text += `🛠️ RADAR DE FERRAMENTAS & REPOSITÓRIOS (${currentData.tools.length}):\n`;
    currentData.tools.slice(0, 5).forEach((t, i) => {
      text += `${i + 1}. ${t.title} [${t.pricing_model || 'Grátis'}]\n   -> ${t.summary || ''}\n   -> Link: ${t.canonical_url}\n\n`;
    });
  }

  if (currentData.opportunities.length > 0) {
    text += `💡 OPORTUNIDADES DE NEGÓCIO & MONETIZAÇÃO (${currentData.opportunities.length}):\n`;
    currentData.opportunities.slice(0, 5).forEach((o, i) => {
      text += `${i + 1}. ${o.title}\n   -> Como lucrar/aplicar: ${o.why_it_matters || o.summary}\n   -> Link: ${o.canonical_url}\n\n`;
    });
  }

  if (currentData.business.length > 0) {
    text += `💼 BUSINESS, STARTUPS & INVESTIMENTOS (${currentData.business.length}):\n`;
    currentData.business.slice(0, 5).forEach((b, i) => {
      text += `${i + 1}. ${b.title}\n   -> Análise: ${b.why_it_matters || b.summary}\n   -> Link: ${b.canonical_url}\n\n`;
    });
  }

  navigator.clipboard.writeText(text).then(() => {
    showToast('📋 Resumo Executivo copiado para a área de transferência!');
  }).catch(err => {
    showToast('Erro ao copiar resumo.');
  });
}

function downloadMarkdownReport() {
  const dateStr = dateSelect.value || new Date().toISOString().split('T')[0];
  const filename = `maclovin-briefing-${dateStr}.md`;
  
  let md = `# Maclovin Intelligence Briefing — ${dateStr}\n\n`;
  ['tools', 'opportunities', 'business', 'news', 'learning', 'geek'].forEach(tab => {
    const list = currentData[tab] || [];
    if (list.length > 0) {
      md += `## ${tab.toUpperCase()}\n\n`;
      list.forEach((item, idx) => {
        md += `### ${idx + 1}. ${item.title}\n`;
        md += `**Fonte:** \`${item.source_id}\` | **Link:** [${item.canonical_url}](${item.canonical_url})\n\n`;
        md += `> ${item.summary || item.title}\n\n`;
        if (item.why_it_matters) md += `💡 **Takeaway:** ${item.why_it_matters}\n\n`;
      });
    }
  });

  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  showToast(`📥 Relatório ${filename} baixado com sucesso!`);
}

function downloadJsonData() {
  const dateStr = dateSelect.value || new Date().toISOString().split('T')[0];
  const blob = new Blob([JSON.stringify(currentData, null, 2)], { type: 'application/json;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `maclovin-${dateStr}.json`;
  a.click();
  showToast(`💾 Arquivo JSON baixado com sucesso!`);
}

function renderCards() {
  cardsGrid.innerHTML = '';
  let items = currentData[activeTab] || [];

  // Filtro de subtipo contextual
  if (activeSubfilter !== 'all') {
    items = items.filter(item => {
      const text = `${item.title} ${item.summary || ''} ${item.why_it_matters || ''}`.toLowerCase();
      if (activeTab === 'tools') {
        return item.tool_subtype === activeSubfilter;
      } else if (activeTab === 'opportunities') {
        if (activeSubfilter === 'enterprise') return text.includes('empresa') || text.includes('enterprise') || text.includes('automação') || text.includes('b2b');
        if (activeSubfilter === 'microsaas') return text.includes('saas') || text.includes('micro') || text.includes('monetizar') || text.includes('vender');
      } else if (activeTab === 'business') {
        if (activeSubfilter === 'funding') return text.includes('funding') || text.includes('aporte') || text.includes('rodada') || text.includes('investimento');
        if (activeSubfilter === 'ma') return text.includes('m&a') || text.includes('aquisição') || text.includes('comprou') || text.includes('comprar');
        if (activeSubfilter === 'market') return text.includes('lucro') || text.includes('receita') || text.includes('quarter') || text.includes('big tech');
      } else if (activeTab === 'news') {
        if (activeSubfilter === 'models') return text.includes('modelo') || text.includes('gpt') || text.includes('claude') || text.includes('gemini') || text.includes('llama') || text.includes('deepseek');
        if (activeSubfilter === 'regulation') return text.includes('processo') || text.includes('regulação') || text.includes('governo') || text.includes('multa');
      } else if (activeTab === 'learning') {
        if (activeSubfilter === 'tutorials') return text.includes('tutorial') || text.includes('guia') || text.includes('como');
        if (activeSubfilter === 'architecture') return text.includes('arquitetura') || text.includes('sistema') || text.includes('engenharia') || text.includes('paper');
      } else if (activeTab === 'geek') {
        if (activeSubfilter === 'games') return text.includes('game') || text.includes('jogo') || text.includes('playstation') || text.includes('steam') || text.includes('switch');
        if (activeSubfilter === 'movies') return text.includes('filme') || text.includes('cinema') || text.includes('trailer') || text.includes('série');
        if (activeSubfilter === 'comics') return text.includes('hq') || text.includes('quadrinho') || text.includes('comic') || text.includes('mangá');
      }
      return true;
    });
  }

  // Filtro de preço (ferramentas)
  if (activeTab === 'tools' && activePricing !== 'all') {
    items = items.filter(item => {
      const p = (item.pricing_model || '').toLowerCase();
      if (activePricing === 'free') return p.includes('grátis') || p.includes('open-source') || p.includes('free');
      if (activePricing === 'freemium') return p.includes('freemium');
      if (activePricing === 'paid') return p.includes('pago') || p.includes('paid') || p.includes('comercial');
      return true;
    });
  }

  // Filtro de fonte
  if (activeSource !== 'all') {
    items = items.filter(item => item.source_id === activeSource);
  }

  // Filtro de busca textual
  if (searchQuery) {
    items = items.filter(item => {
      const text = `${item.title} ${item.summary || ''} ${item.why_it_matters || ''} ${(item.key_features || []).join(' ')} ${item.source_id || ''}`.toLowerCase();
      return text.includes(searchQuery);
    });
  }

  // Ordenação
  if (activeSort === 'az') {
    items.sort((a, b) => a.title.localeCompare(b.title));
  } else if (activeSort === 'relevance') {
    items.sort((a, b) => (b.relevance_score || 0) - (a.relevance_score || 0));
  } else if (activeSort === 'recent') {
    items.sort((a, b) => (b.published_date_utc || '').localeCompare(a.published_date_utc || ''));
  }

  if (items.length === 0) {
    emptyState.classList.remove('hidden');
    return;
  } else {
    emptyState.classList.add('hidden');
  }

  items.forEach(item => {
    const card = document.createElement('article');
    card.className = 'editorial-card';

    const subtypeBadge = activeTab === 'tools' ? getSubtypeBadge(item.tool_subtype) : '';
    const pricingBadge = (activeTab === 'tools' || item.pricing_model) ? getPricingBadge(item.pricing_model) : '';
    
    let takeawayLabel = 'Contexto & Impacto:';
    if (activeTab === 'opportunities') takeawayLabel = '💰 Como Lucrar ou Aplicar na Empresa:';
    else if (activeTab === 'business') takeawayLabel = '📈 Análise de Mercado:';

    const takeawayBox = item.why_it_matters ? `
      <div class="card-takeaway">
        <strong>${takeawayLabel}</strong> ${item.why_it_matters}
      </div>
    ` : '';

    let featuresHtml = '';
    if (item.key_features && item.key_features.length > 0) {
      featuresHtml = `
        <div class="card-tags">
          ${item.key_features.map(f => `<span class="feature-pill">✔ ${f}</span>`).join('')}
        </div>
      `;
    }

    let timeFormatted = '12:00';
    if (item.published_date_utc) {
      try {
        const pubDate = new Date(item.published_date_utc);
        timeFormatted = pubDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } catch (e) {
        timeFormatted = '12:00';
      }
    }

    let ctaLabel = 'Ler matéria completa ↗';
    if (activeTab === 'tools') {
      ctaLabel = item.tool_subtype === 'repo' ? 'Ver no GitHub ↗' : 'Acessar ferramenta ↗';
    } else if (activeTab === 'opportunities') {
      ctaLabel = 'Explorar oportunidade ↗';
    }

    const thumbHtml = item.thumbnail_url
      ? `<div class="card-thumb" style="background-image:url('${item.thumbnail_url}')"></div>`
      : '';

    card.innerHTML = `
      ${thumbHtml}
      <div>
        <div class="card-top">
          <div class="card-badges-left">
            <span class="card-source-pill">${item.source_id || 'Fonte'}</span>
            ${subtypeBadge}
          </div>
          ${pricingBadge}
        </div>
        <h3 class="card-headline" title="Clique para ver os detalhes">${item.title}</h3>
        <p class="card-lead">${item.summary || item.title}</p>
        ${takeawayBox}
        ${featuresHtml}
      </div>
      <div class="card-action-bar">
        <div class="card-action-bar-left">
          <a href="${item.canonical_url || '#'}" target="_blank" rel="noopener noreferrer" class="read-btn">
            ${ctaLabel}
          </a>
          <button class="read-btn" style="color:var(--text-muted);font-weight:500" data-modal="true">
            📖 Detalhes
          </button>
        </div>
        <span class="card-pubtime">${timeFormatted} UTC</span>
      </div>
    `;

    // Click handler for modal view
    const headline = card.querySelector('.card-headline');
    const modalBtn = card.querySelector('[data-modal="true"]');
    if (headline) headline.addEventListener('click', () => openModalWithItem(item));
    if (modalBtn) modalBtn.addEventListener('click', () => openModalWithItem(item));

    cardsGrid.appendChild(card);
  });
}
