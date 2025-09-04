window.XPLAB = (() => {
  const CONFIG_URL = "/_assets/portal.config.json";

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const withTimeout = (p, ms = 6000) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), ms))]);

  async function loadConfig(opts = {}) {
    const res = await withTimeout(fetch(CONFIG_URL, { cache: 'no-cache' }));
    if (!res.ok) throw new Error("config load failed");
    const cfg = await res.json();
    if (opts.portal && cfg?.appearance?.theme === 'auto') applyAutoTheme();
    return cfg;
  }

  function filterTiles(cfg, predicate) {
    return (cfg.sections.find(s => s.id === 'nav')?.tiles || []).filter(predicate);
  }

  function renderTiles(root, tiles) {
    root.innerHTML = "";
    tiles.forEach(t => {
      const a = document.createElement('a');
      a.className = 'tile';
      a.href = t.href;
      a.target = t.target || '_self';
      a.rel = 'noopener';
      a.innerHTML = `
        <div class="tile-icon">${iconFor(t.icon) ?? '🔗'}</div>
        <div class="tile-title">${escapeHTML(t.label)}</div>
        <div class="tile-desc">${escapeHTML(t.desc || '')}</div>`;
      root.appendChild(a);
    });
  }

  function renderBadges(root, widgets) {
    root.innerHTML = "";
    widgets.forEach(w => {
      const badge = document.createElement('div');
      badge.className = 'badge dot';
      badge.innerHTML = `<strong>${escapeHTML(w.label)}</strong><span class="muted">loading…</span>`;
      root.appendChild(badge);
      if (w.type === 'badge' && w.source) {
        // Fetch HA proxy (expects Home Assistant JSON state shape)
        fetchJSON(w.source).then(s => {
          const state = s?.state;
          const c = state === 'on' || state === 'ok' ? 'ok' : (state === 'unknown' ? 'warn' : 'err');
          badge.classList.add(c);
          badge.lastElementChild.textContent = state ?? 'unknown';
        }).catch(() => {
          badge.classList.add('err');
          badge.lastElementChild.textContent = 'unreachable';
        });
      }
    });
  }

  function iconFor(name) {
    const map = {
      nas: '💾', ha: '🏠', grafana: '📊', plex: '🎬', jellyfin: '🍿', tailscale: '🌀',
      node: '🟩', docs: '📚', files: '📁', tools: '🧰', link: '🔗', media: '🎞️'
    };
    return map[name] || '🔗';
  }

  function escapeHTML(s) { return s?.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m])) || ""; }

  async function fetchJSON(url, opts = {}) {
    const res = await withTimeout(fetch(url, { headers: { 'accept': 'application/json' }, ...opts }));
    if (!res.ok) throw new Error(res.statusText);
    return res.json();
  }

  function applyAutoTheme() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    setTheme(prefersDark.matches ? 'dark' : 'light');
    prefersDark.addEventListener('change', (e) => setTheme(e.matches ? 'dark' : 'light'));
  }

  function setTheme(mode /* 'light'|'dark' */) {
    document.documentElement.classList.remove('theme-light', 'theme-dark');
    document.documentElement.classList.add(`theme-${mode}`);
    localStorage.setItem('xplab_theme', mode);
  }

  function initTheme(cfg) {
    const stored = localStorage.getItem('xplab_theme');
    if (stored) setTheme(stored);
    else if (cfg?.appearance?.theme === 'auto') applyAutoTheme();
    else if (cfg?.appearance?.theme) setTheme(cfg.appearance.theme);
    // Optional HA-driven theme override
    const entity = cfg?.appearance?.haThemeEntity;
    if (entity) observeHaTheme(entity);
  }

  async function observeHaTheme(entityId) {
    const url = `/ha/api/states/${encodeURIComponent(entityId)}`;
    // Poll gently; avoid WS complexity for now
    for (; ;) {
      try {
        const j = await fetchJSON(url);
        const v = (j?.state || '').toLowerCase();
        if (v === 'light' || v === 'dark') setTheme(v);
        if (v === 'auto') applyAutoTheme();
      } catch (_) { }
      await sleep(10000);
    }
  }

  function bindThemeToggle(btn) {
    btn?.addEventListener('click', () => {
      const now = document.documentElement.classList.contains('theme-dark') ? 'light' : 'dark';
      setTheme(now);
    });
  }

  function updateGreeting(elId) {
    const el = document.getElementById(elId);
    const h = new Date().getHours();
    const slot = h < 12 ? "morning" : h < 18 ? "afternoon" : "evening";
    el.textContent = `Good ${slot} — Ops Console`;
  }

  async function observePresence(entityId, elId) {
    const el = document.getElementById(elId);
    if (!entityId) { el.textContent = 'Presence: n/a'; return; }
    for (; ;) {
      try {
        const j = await fetchJSON(`/ha/api/states/${encodeURIComponent(entityId)}`);
        el.textContent = `Presence: ${j?.state ?? 'unknown'}`;
      } catch (_) { el.textContent = 'Presence: unreachable'; }
      await sleep(10000);
    }
  }

  return {
    loadConfig, filterTiles, renderTiles, renderBadges,
    initTheme, bindThemeToggle, updateGreeting, observePresence
  };
})();
