// MACLOVIN NEWS — Editorial Frontend Logic & Strict Categorization

let rawBriefingData = null;
let currentData = {
  tools: [],
  news: [],
  learning: [],
  geek: [],
};

let activeTab = 'tools';
let activePricing = 'all';
let searchQuery = '';

// DOM Elements
const dateSelect = document.getElementById('dateSelect');
const btnSync = document.getElementById('btnSync');
const searchInput = document.getElementById('searchInput');
const clearSearch = document.getElementById('clearSearch');
const pricingFilters = document.getElementById('pricingFilters');
const cardsGrid = document.getElementById('cardsGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const footerStats = document.getElementById('footerStats');
const currentDateDisplay = document.getElementById('currentDateDisplay');

const badgeTools = document.getElementById('badgeTools');
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

const TOOL_KW = [
  'tool', 'ferramenta', 'software', 'open-source', 'open source', 'código aberto', 'github', 'repositório',
  'repository', 'library', 'biblioteca', 'framework', 'saas', 'extension', 'extensão', 'plugin', 'sdk', 'api',
  'npm', 'pypi', 'docker', 'qwen', 'llama', 'whisper', 'claude code', 'cursor', 'ollama', 'vllm', 'langchain'
];

function classifyItemStrict(item) {
  const text = `${item.title || ''} ${item.summary || ''} ${item.source_id || ''}`.toLowerCase();
  
  // 1. Geek & Games prioritário (impede games em ferramentas)
  for (const kw of GEEK_KW) {
    if (text.includes(kw)) return 'geek';
  }
  
  // 2. Aprender & Deep Dives
  for (const kw of LEARNING_KW) {
    if (text.includes(kw)) return 'learning';
  }
  
  // 3. Ferramentas reais de software
  for (const kw of TOOL_KW) {
    if (text.includes(kw)) return 'tools';
  }
  
  // 4. Default por tipo ou notícia
  if (item.item_type === 'tool' && !GEEK_KW.some(k => text.includes(k))) return 'tools';
  if (item.item_type === 'learning') return 'learning';
  if (item.item_type === 'geek') return 'geek';

  return 'news';
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
      
      // Filtros de preço apenas na aba de ferramentas
      if (activeTab === 'tools') {
        pricingFilters.classList.remove('hidden');
      } else {
        pricingFilters.classList.add('hidden');
      }

      renderCards();
    });
  });

  // Pricing Chips
  document.querySelectorAll('.filter-tag').forEach(tag => {
    tag.addEventListener('click', () => {
      document.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
      tag.classList.add('active');
      activePricing = tag.dataset.pricing;
      renderCards();
    });
  });

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

  // Date Change
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
        if (payload.tools || payload.news || payload.learning || payload.geek) {
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
  rawBriefingData = data;
  
  // Reorganizar deterministicamente todos os itens para garantir pureza de categoria
  const allItems = [
    ...(data.tools || []),
    ...(data.news || []),
    ...(data.learning || []),
    ...(data.geek || []),
  ];

  const tools = [];
  const news = [];
  const learning = [];
  const geek = [];

  allItems.forEach(it => {
    const cat = classifyItemStrict(it);
    it.item_type = cat === 'tools' ? 'tool' : cat;
    if (cat === 'tools') tools.push(it);
    else if (cat === 'learning') learning.push(it);
    else if (cat === 'geek') geek.push(it);
    else news.push(it);
  });

  currentData.tools = tools;
  currentData.news = news;
  currentData.learning = learning;
  currentData.geek = geek;

  // Atualizar badges dos contadores
  badgeTools.textContent = currentData.tools.length;
  badgeNews.textContent = currentData.news.length;
  badgeLearning.textContent = currentData.learning.length;
  badgeGeek.textContent = currentData.geek.length;

  // Formatar data de exibição
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
      opt.textContent = 'Edição de Hoje';
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

  try {
    let url = date ? `/api/briefing?date=${date}` : '/api/briefing';
    let res = await fetch(url);
    if (!res.ok) {
      res = await fetch('/data/briefing.json');
    }
    const data = await res.json();
    applyData(data);
  } catch (err) {
    console.error('Erro ao carregar briefing:', err);
  } finally {
    loadingState.classList.add('hidden');
  }
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

  // Filtro de preço (apenas na aba de ferramentas)
  if (activeTab === 'tools' && activePricing !== 'all') {
    items = items.filter(item => {
      const p = (item.pricing_model || '').toLowerCase();
      if (activePricing === 'free') return p.includes('grátis') || p.includes('open-source') || p.includes('free');
      if (activePricing === 'freemium') return p.includes('freemium');
      if (activePricing === 'paid') return p.includes('pago') || p.includes('paid');
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

    const pricingBadge = (activeTab === 'tools' || item.pricing_model) ? getPricingBadge(item.pricing_model) : '';
    const takeawayBox = item.why_it_matters ? `
      <div class="card-takeaway">
        <strong>Contexto & Impacto:</strong> ${item.why_it_matters}
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

    card.innerHTML = `
      <div>
        <div class="card-top">
          <span class="card-source-pill">${item.source_id || 'Fonte'}</span>
          ${pricingBadge}
        </div>
        <h3 class="card-headline">${item.title}</h3>
        <p class="card-lead">${item.summary || item.title}</p>
        ${takeawayBox}
        ${featuresHtml}
      </div>
      <div class="card-action-bar">
        <a href="${item.canonical_url || '#'}" target="_blank" rel="noopener noreferrer" class="read-btn">
          Ler matéria completa ↗
        </a>
        <span class="card-pubtime">${timeFormatted} UTC</span>
      </div>
    `;

    cardsGrid.appendChild(card);
  });
}
