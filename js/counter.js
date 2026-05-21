/* View counter — powered by Supabase */
(async function () {
  'use strict';

  /* ── Guard: Supabase not configured ── */
  const cfg = window.SUPABASE_CONFIG;
  const notConfigured =
    !cfg ||
    cfg.url.includes('YOUR_PROJECT_ID') ||
    cfg.anonKey.includes('YOUR_ANON');

  if (notConfigured) {
    document.querySelectorAll('[data-path]').forEach(function (el) {
      el.textContent = '—';
    });
    return;
  }

  /* ── Guard: Supabase SDK not loaded ── */
  if (typeof supabase === 'undefined' || typeof supabase.createClient !== 'function') {
    console.warn('[counter] @supabase/supabase-js not loaded');
    return;
  }

  const client = supabase.createClient(cfg.url, cfg.anonKey);

  /* ── Normalise current path ── */
  var raw = window.location.pathname;
  if (raw === '' || raw === '/index.html') raw = '/';
  var currentPath = raw.endsWith('/') ? raw : raw + '/';

  /* ── Increment current page (skip on localhost) ── */
  var isLocal =
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1';

  var incrementedCount = null;
  if (!isLocal) {
    var rpcResult = await client.rpc('increment_page_view', { page_path: currentPath });
    if (!rpcResult.error && rpcResult.data !== null) {
      incrementedCount = Number(rpcResult.data);
    }
  }

  /* ── Collect all data-path elements ── */
  var els = Array.from(document.querySelectorAll('[data-path]'));
  if (els.length === 0) return;

  var paths = Array.from(new Set(els.map(function (el) { return el.dataset.path; })));

  /* ── Apply incremented count for current page immediately ── */
  function applyCount(el, count) {
    var n = Number(count) || 0;
    el.textContent =
      el.classList.contains('card-views') || el.dataset.format === 'card'
        ? n.toLocaleString('zh-TW') + ' 次'
        : n.toLocaleString('zh-TW');
  }

  if (incrementedCount !== null) {
    els
      .filter(function (el) { return el.dataset.path === currentPath; })
      .forEach(function (el) { applyCount(el, incrementedCount); });
  }

  /* ── Fetch remaining paths ── */
  var otherPaths = paths.filter(function (p) { return p !== currentPath; });
  var allFetchPaths = isLocal ? paths : otherPaths;

  if (allFetchPaths.length === 0) return;

  var fetchResult = await client
    .from('page_views')
    .select('path, views')
    .in('path', allFetchPaths);

  if (fetchResult.error) {
    console.warn('[counter] fetch error', fetchResult.error);
    return;
  }

  var viewMap = {};
  (fetchResult.data || []).forEach(function (row) {
    viewMap[row.path] = row.views;
  });

  els
    .filter(function (el) { return allFetchPaths.indexOf(el.dataset.path) !== -1; })
    .forEach(function (el) {
      applyCount(el, viewMap[el.dataset.path] || 0);
    });
})();
