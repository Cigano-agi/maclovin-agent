// Frontend Dashboard Application Logic

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
const pricingFilters = document.getElementById('pricingFilters');
const cardsGrid = document.getElementById('cardsGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const footerStats = document.getElementById('footerStats');

const badgeTools = document.getElementById('badgeTools');
const badgeNews = document.getElementById('badgeNews');
const badgeLearning = document.getElementById('badgeLearning');
const badgeGeek = document.getElementById('badgeGeek');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await loadHistoryDates();
  await fetchBriefing();
});

function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activeTab = tab.dataset.tab;
      
      // Mostrar filtros de preço apenas na aba de ferramentas
      if (activeTab === 'tools') {
        pricingFilters.classList.remove('hidden');
      } else {
        pricingFilters.classList.add('hidden');
      }

      renderCards();
    });
  });

  // Pricing Chips
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activePricing = chip.dataset.pricing;
      renderCards();
    });
  });

  // Search Input
  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value.toLowerCase().trim();
    renderCards();
  });

  // Date Change
  dateSelect.addEventListener('change', () => {
    fetchBriefing(dateSelect.value);
  });

  // Sync Button
  btnSync.addEventListener('click', async () => {
    btnSync.disabled = true;
    btnSync.innerHTML = `<span class="spinner" style="width:14px;height:14px;border-width:2px;display:inline-block;margin:0"></span> Sincronizando...`;
    
    try {
      const res = await fetch('/api/run', { method: 'POST' });
      if (res.ok) {
        await loadHistoryDates();
        await fetchBriefing();
      }
    } catch (err) {
      console.error('Falha na sincronização:', err);
    } finally {
      btnSync.disabled = false;
      btnSync.innerHTML = `<span class="sync-icon">⚡</span> Sincronizar Agora`;
    }
  });
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
        opt.textContent = d;
        dateSelect.appendChild(opt);
      });
    } else {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'Ontem';
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

    currentData.tools = data.tools || [];
    currentData.news = data.news || [];
    currentData.learning = data.learning || [];
    currentData.geek = data.geek || [];

    // Atualizar badges
    badgeTools.textContent = currentData.tools.length;
    badgeNews.textContent = currentData.news.length;
    badgeLearning.textContent = currentData.learning.length;
    badgeGeek.textContent = currentData.geek.length;

    // Atualizar footer
    const stats = data.latest_execution;
    if (stats) {
      footerStats.innerHTML = `📅 <strong>Data:</strong> ${data.date} &bull; 📊 <strong>Total de Itens:</strong> ${data.total_items} &bull; ⚡ <strong>Status:</strong> <span style="color:#10B981">${stats.status}</span>`;
    } else {
      footerStats.innerHTML = `📅 <strong>Data:</strong> ${data.date} &bull; 📊 <strong>Total de Itens:</strong> ${data.total_items}`;
    }

    renderCards();
  } catch (err) {
    console.error('Erro ao buscar dados:', err);
  } finally {
    loadingState.classList.add('hidden');
  }
}

function getBadgeClass(pricing) {
  const p = (pricing || '').toLowerCase();
  if (p.includes('grátis') || p.includes('open-source') || p.includes('free')) return 'badge-free';
  if (p.includes('freemium')) return 'badge-freemium';
  if (p.includes('pago') || p.includes('paid')) return 'badge-paid';
  return 'badge-unspecified';
}

function renderCards() {
  cardsGrid.innerHTML = '';
  let items = currentData[activeTab] || [];

  // Filtro de preço (apenas se for aba de ferramentas)
  if (activeTab === 'tools' && activePricing !== 'all') {
    items = items.filter(item => {
      const p = (item.pricing_model || '').toLowerCase();
      if (activePricing === 'free') return p.includes('grátis') || p.includes('open-source') || p.includes('free');
      if (activePricing === 'freemium') return p.includes('freemium');
      if (activePricing === 'paid') return p.includes('pago') || p.includes('paid');
      return true;
    });
  }

  // Filtro de busca
  if (searchQuery) {
    items = items.filter(item => {
      const text = `${item.title} ${item.summary || ''} ${item.why_it_matters || ''} ${(item.key_features || []).join(' ')}`.toLowerCase();
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
    const card = document.createElement('div');
    card.className = 'card';

    const pricingBadge = item.pricing_model ? `<span class="card-badge ${getBadgeClass(item.pricing_model)}">${item.pricing_model}</span>` : '';
    const whyBox = item.why_it_matters ? `<div class="card-why">💡 <strong>Por que importa:</strong> ${item.why_it_matters}</div>` : '';
    
    let featuresHtml = '';
    if (item.key_features && item.key_features.length > 0) {
      featuresHtml = `
        <div class="card-features">
          ${item.key_features.map(f => `<span class="feature-tag">✔ ${f}</span>`).join('')}
        </div>
      `;
    }

    const pubDate = new Date(item.published_date_utc);
    const timeFormatted = pubDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    card.innerHTML = `
      <div>
        <div class="card-header">
          <span class="card-source">${item.source_id}</span>
          ${pricingBadge}
        </div>
        <h3 class="card-title">${item.title}</h3>
        <p class="card-summary">${item.summary || item.title}</p>
        ${whyBox}
        ${featuresHtml}
      </div>
      <div class="card-footer">
        <a href="${item.canonical_url}" target="_blank" rel="noopener noreferrer" class="card-link">
          Acessar link original ↗
        </a>
        <span class="card-time">${timeFormatted} UTC</span>
      </div>
    `;

    cardsGrid.appendChild(card);
  });
}
