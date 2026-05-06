/**
 * dashboard.js  —  Spotify 2023 EDA Dashboard
 * =============================================
 * Fetches chart data from Flask API endpoints,
 * renders interactive Plotly charts, and handles
 * tab switching + responsive resizing.
 */

// ─────────────────────────────────────────────
// CONFIG: every chart endpoint + its target div
// ─────────────────────────────────────────────
const CHARTS = [
  // [tab, endpoint-key, plot-div-id]
  ['popularity', 'top_tracks',         'plot-top_tracks'],
  ['popularity', 'top_artists',        'plot-top_artists'],
  ['popularity', 'streams_dist',       'plot-streams_dist'],
  ['popularity', 'popularity_tier',    'plot-popularity_tier'],
  ['popularity', 'outliers',           'plot-outliers'],

  ['temporal',   'yearly_trend',       'plot-yearly_trend'],
  ['temporal',   'monthly_releases',   'plot-monthly_releases'],

  ['audio',      'correlation',        'plot-correlation'],
  ['audio',      'dance_energy',       'plot-dance_energy'],
  ['audio',      'valence_energy',     'plot-valence_energy'],
  ['audio',      'feature_boxplots',   'plot-feature_boxplots'],
  ['audio',      'mood_dist',          'plot-mood_dist'],
  ['audio',      'bpm_dist',           'plot-bpm_dist'],
  ['audio',      'bpm_dance',          'plot-bpm_dance'],
  ['audio',      'energy_mode',        'plot-energy_mode'],
  ['audio',      'acoustic_instrument','plot-acoustic_instrument'],
  ['audio',      'live_speech',        'plot-live_speech'],
  ['audio',      'key_dist',           'plot-key_dist'],
  ['audio',      'mode_pie',           'plot-mode_pie'],
  ['audio',      'key_streams',        'plot-key_streams'],

  ['platforms',  'platform_compare',   'plot-platform_compare'],

  ['stats',      'stats_table',        'plot-stats_table'],
];

// Track which charts have already been loaded (lazy loading)
const loaded = new Set();

// Plotly default config (removes Plotly logo, adds responsive mode)
const PLOTLY_CONFIG = {
  responsive: true,
  displayModeBar: true,
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
  displaylogo: false,
  toImageButtonOptions: { format: 'png', filename: 'spotify_eda_chart', scale: 2 },
};

// ─────────────────────────────────────────────
// FETCH SUMMARY CARDS
// ─────────────────────────────────────────────
async function loadSummary() {
  try {
    const res  = await fetch('/api/summary');
    const data = await res.json();

    // Animate numbers counting up
    animateValue('val-tracks',    data.total_tracks,    true);
    animateValue('val-artists',   data.total_artists,   true);
    setText('val-streams',   data.total_streams);
    setText('val-bpm',       data.avg_bpm);
    setText('val-dance',     data.avg_danceability);
    setText('val-energy',    data.avg_energy);
    setText('val-top-artist',data.top_artist);
    setText('val-top-track', data.top_track);
    setText('val-year',      data.year_range);
    setText('val-missing',   `${data.missing_before} → ${data.missing_after}`);
  } catch (err) {
    console.error('Failed to load summary:', err);
  }
}

// Animate numeric counter
function animateValue(id, target, isInt = false) {
  const el = document.getElementById(id);
  if (!el) return;
  const duration = 1200;
  const startTime = performance.now();
  function update(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased    = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current  = isInt ? Math.round(eased * target) : (eased * target).toFixed(1);
    el.textContent = Number(current).toLocaleString();
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? '—';
}

// ─────────────────────────────────────────────
// FETCH & RENDER A SINGLE CHART
// ─────────────────────────────────────────────
async function renderChart(endpoint, divId) {
  const container = document.getElementById(divId);
  if (!container) return;

  // Show spinner while loading
  container.innerHTML = '<div class="spinner">Loading chart…</div>';

  try {
    const res  = await fetch(`/api/chart/${endpoint}`);
    const data = await res.json();

    // Clear spinner
    container.innerHTML = '';

    // Plotly.newPlot(div, data, layout, config)
    Plotly.newPlot(container, data.data, data.layout, PLOTLY_CONFIG);
  } catch (err) {
    container.innerHTML = `<div class="spinner" style="color:#ef4444">⚠️ Failed to load chart</div>`;
    console.error(`Chart [${endpoint}] error:`, err);
  }
}

// ─────────────────────────────────────────────
// LAZY-LOAD CHARTS FOR THE ACTIVE TAB
// ─────────────────────────────────────────────
function loadChartsForTab(tabName) {
  CHARTS
    .filter(([tab]) => tab === tabName)
    .forEach(([, endpoint, divId]) => {
      if (!loaded.has(endpoint)) {
        loaded.add(endpoint);
        renderChart(endpoint, divId);
      }
    });
}

// ─────────────────────────────────────────────
// TAB SWITCHING LOGIC
// ─────────────────────────────────────────────
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanels  = document.querySelectorAll('.tab-panel');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.dataset.tab;

      // Update button active states
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Show/hide panels
      tabPanels.forEach(panel => {
        panel.classList.remove('active');
        if (panel.id === `tab-${targetTab}`) {
          panel.classList.add('active');
        }
      });

      // Lazy-load charts for the newly activated tab
      loadChartsForTab(targetTab);

      // After panel is visible, trigger Plotly resize so charts fill correctly
      setTimeout(() => {
        document.querySelectorAll(`#tab-${targetTab} .chart-placeholder`).forEach(el => {
          Plotly.Plots && Plotly.Plots.resize && Plotly.Plots.resize(el);
        });
      }, 100);
    });
  });
}

// ─────────────────────────────────────────────
// RESIZE HANDLER: re-fit charts on window resize
// ─────────────────────────────────────────────
function initResizeHandler() {
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      document.querySelectorAll('.chart-placeholder').forEach(el => {
        if (el.data) Plotly.Plots.resize(el); // only resize rendered charts
      });
    }, 250);
  });
}

// ─────────────────────────────────────────────
// MAIN: kick everything off when DOM is ready
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // 1. Fetch and display summary cards
  loadSummary();

  // 2. Wire up tab click handlers
  initTabs();

  // 3. Handle window resize
  initResizeHandler();

  // 4. Load charts for the default active tab ("popularity")
  loadChartsForTab('popularity');
});
