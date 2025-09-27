// _assets/app.js — minimal resilient config fetch with AbortController + exponential backoff
(function(){
  'use strict';
  const manifestVersion = null; // Replace during build or keep null to rely on no-store
  const configUrlBase = '/_assets/portal.config.json';
  const maxAttempts = 5;
  const baseDelay = 300; // ms

  function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }

  async function fetchWithBackoff(){
    let attempt = 0;
    while(attempt < maxAttempts){
      const controller = new AbortController();
      const signal = controller.signal;
      const url = configUrlBase + (manifestVersion ? `?v=${encodeURIComponent(manifestVersion)}` : '');
      try{
        const timeout = setTimeout(()=>controller.abort(), 5000 + attempt*2000);
        const res = await fetch(url, {cache: 'no-store', credentials: 'same-origin', signal});
        clearTimeout(timeout);
        if(res && res.ok){
          const json = await res.json();
          window.__PORTAL_CONFIG = json;
          return json;
        }
      }catch(e){
        // retry
      }
      attempt++;
      await sleep(baseDelay * Math.pow(2, attempt));
    }
    return null;
  }

  // Gate iframe loads until /portal/ping.html returns 200
  async function portalAuthPing(){
    try{
      const r = await fetch('/portal/ping.html', {cache: 'no-store', credentials: 'same-origin'});
      return r && r.ok;
    }catch(e){ return false; }
  }

  async function init(){
    const cfg = await fetchWithBackoff();
    const ok = await portalAuthPing();
    if(!ok){ console.warn('portal auth ping failed; delaying iframe loads'); }
    // Expose readiness for app code
    window.__PORTAL_READY = { config: cfg, auth: ok };
    // Application can now proceed to render or defer
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
