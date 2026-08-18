// MACLOVIN NEWS — Editorial Frontend Logic, Subtypes, Opportunities, Business & History

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
let activeToolSubtype = 'all'; // 'all', 'repo', 'app'
let activePricing = 'all';     // 'all', 'free', 'freemium', 'paid'
let searchQuery = '';

// DOM Elements
const dateSelect = document.getElementById('dateSelect');
const btnSync = document.getElementById('btnSync');
const searchInput = document.getElementById('searchInput');
const clearSearch = document.getElementById('clearSearch');
const toolSubtypeFilters = document.getElementById('toolSubtypeFilters');
const pricingFilters = document.getElementById('pricingFilters');
const cardsGrid = document.getElementById('cardsGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const footerStats = document.getElementById('footerStats');
const currentDateDisplay = document.getElementById('currentDateDisplay');

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
  
  // 1. Geek & Games prioritário
  for (const kw of GEEK_KW) {
    if (text.includes(kw)) return 'geek';
  }
  
  // 2. Oportunidades & Monetização
  for (const kw of OPPORTUNITY_KW) {
    if (text.includes(kw)) return 'opportunities';
  }

  // 3. Aprender & Deep Dives
  for (const kw of LEARNING_KW) {
    if (text.includes(kw)) return 'learning';
  }

  // 4. Business, Startups & Investimentos
  for (const kw of BUSINESS_KW) {
    if (text.includes(kw)) return 'business';
  }
  
  // 5. Ferramentas reais
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
  await loadHistoryDates();
  await fetchBriefing();
});

function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeTab = btn.dataset.tab;
      
      // Mostrar filtros de subtipo e preço apenas na aba de ferramentas
      if (activeTab === 'tools') {
        if (toolSubtypeFilters) toolSubtypeFilters.classList.remove('hidden');
        if (pricingFilters) pricingFilters.classList.remove('hidden');
      } else {
        if (toolSubtypeFilters) toolSubtypeFilters.classList.add('hidden');
        if (pricingFilters) pricingFilters.classList.add('hidden');
      }

      renderCards();
    });
  });

  // Tool Subtype Chips (Repos vs Apps)
  if (toolSubtypeFilters) {
    toolSubtypeFilters.querySelectorAll('.filter-tag').forEach(tag => {
      tag.addEventListener('click', () => {
        toolSubtypeFilters.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
        tag.classList.add('active');
        activeToolSubtype = tag.dataset.subtype;
        renderCards();
      });
    });
  }

  // Pricing Chips
  if (pricingFilters) {
    pricingFilters.querySelectorAll('.filter-tag').forEach(tag => {
      tag.addEventListener('click', () => {
        pricingFilters.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
        tag.classList.add('active');
        activePricing = tag.dataset.pricing;
        renderCards();
      });
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
        if (payload.tools || payload.opportunities || payload.business || payload.news || payload.learning || payload.geek) {
          applyData(payload);
        } else {
          await loadHistoryDates();
          await fetchBriefing();
        }
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

  allItems.forEach(it => {
    const cat = classifyItemStrict(it);
    it.item_type = cat === 'tools' ? 'tool' : cat;
    it.tool_subtype = detectToolSubtype(it);
    
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
  const stats = data.latest_execution;
  if (stats) {
    footerStats.innerHTML = `📅 <strong>Data:</strong> ${data.date} &bull; 📊 <strong>Total de Matérias:</strong> ${allItems.length} &bull; ⚡ <strong>Status:</strong> <span style="color:#10B981">${stats.status}</span>`;
  } else {
    footerStats.innerHTML = `📅 <strong>Data:</strong> ${data.date} &bull; 📊 <strong>Total de Matérias:</strong> ${allItems.length}`;
  }

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

function renderCards() {
  cardsGrid.innerHTML = '';
  let items = currentData[activeTab] || [];

  // Filtro de subtipo (apenas na aba de ferramentas: Todos, Repos, Apps)
  if (activeTab === 'tools' && activeToolSubtype !== 'all') {
    items = items.filter(item => item.tool_subtype === activeToolSubtype);
  }

  // Filtro de preço (apenas na aba de ferramentas)
  if (activeTab === 'tools' && activePricing !== 'all') {
    items = items.filter(item => {
      const p = (item.pricing_model || '').toLowerCase();
      if (activePricing === 'free') return p.includes('grátis') || p.includes('open-source') || p.includes('free');
      if (activePricing === 'freemium') return p.includes('freemium');
      if (activePricing === 'paid') return p.includes('pago') || p.includes('paid') || p.includes('comercial');
      return true;
    });
  }

  // Filtro de busca textual
  if (searchQuery) {
    items = items.filter(item => {
      const text = `${item.title} ${item.summary || ''} ${item.why_it_matters || ''} ${(item.key_features || []).join(' ')} ${item.source_id || ''}`.toLowerCase();
      return text.includes(searchQuery);
    });
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
    else if (activeTab === 'business') takeawayLabel = 'Análise de Mercado:';

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

    card.innerHTML = `
      <div>
        <div class="card-top">
          <div class="card-badges-left">
            <span class="card-source-pill">${item.source_id || 'Fonte'}</span>
            ${subtypeBadge}
          </div>
          ${pricingBadge}
        </div>
        <h3 class="card-headline">${item.title}</h3>
        <p class="card-lead">${item.summary || item.title}</p>
        ${takeawayBox}
        ${featuresHtml}
      </div>
      <div class="card-action-bar">
        <a href="${item.canonical_url || '#'}" target="_blank" rel="noopener noreferrer" class="read-btn">
          ${ctaLabel}
        </a>
        <span class="card-pubtime">${timeFormatted} UTC</span>
      </div>
    `;

    cardsGrid.appendChild(card);
  });
}
