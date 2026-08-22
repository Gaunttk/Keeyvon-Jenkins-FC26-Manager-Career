/* tactical.js — renders docs/depth_chart.html (Tactical Centre) from
   SQUAD_DATA (assets/squad_data.js, generated) and TACTICAL_CONFIG
   (assets/tactical_config.js, hand-curated formation/depth-order).
   Plain script, no build step — same pattern as home.js / squad.js. Runs
   on DOMContentLoaded so it also works opened directly as a file://. */
(function () {
  'use strict';

  function el(tag, className, html) {
    var e = document.createElement(tag);
    if (className) e.className = className;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function placeholderSvg() {
    return '<svg viewBox="0 0 80 88" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
      '<path d="M26,10 L8,14 L0,38 L16,45 L16,82 L64,82 L64,45 L80,38 L72,14 L54,10 L48,12 L40,24 L32,12 Z" ' +
      'fill="currentColor" opacity="0.35"/></svg>';
  }

  function playerHref(p) {
    return 'players/' + p.slug + '.html';
  }

  function byPhoto(cls, p, eager) {
    var wrap = el('div', cls);
    if (p && p.image) {
      var img = el('img');
      img.src = p.image;
      img.alt = p.name;
      img.loading = eager ? 'eager' : 'lazy';
      img.width = 160; img.height = 200;
      wrap.appendChild(img);
    } else {
      wrap.appendChild(el('div', 'tac-photo-placeholder', placeholderSvg()));
    }
    return wrap;
  }

  var SLOT_BUCKET = {
    GK: 'Goalkeeper', LB: 'Defence', CB: 'Defence', RB: 'Defence',
    CM: 'Midfield', CDM: 'Midfield', CAM: 'Midfield',
    LW: 'Attack', ST: 'Attack', RW: 'Attack',
  };
  var BUCKET_ORDER = ['Goalkeeper', 'Defence', 'Midfield', 'Attack'];

  var POSITION_GROUP_ORDER = [
    'Goalkeeper', 'Left Back', 'Right Back', 'Centre Back',
    'Defensive Midfield', 'Central Midfield', 'Attacking Midfield',
    'Left Wing', 'Right Wing', 'Striker',
  ];

  var TIER_LABEL = { starter: 'Starter', rotation: 'Rotation', prospect: 'Prospect' };

  function buildPlayerIndex(data) {
    var idx = {};
    data.players.forEach(function (p) { idx[p.slug] = p; });
    return idx;
  }

  /* ── Tactical Summary ──────────────────────────────────────────────── */
  function renderSummary(root, data, cfg, players) {
    var captain = data.players.find(function (p) { return p.captain; });
    var gkStarter = cfg.starters.find(function (s) { return s.slot === 'GK'; });
    var stStarter = cfg.starters.find(function (s) { return s.slot === 'ST'; });

    var facts = [
      { label: 'Preferred Formation', value: cfg.formation.label },
      cfg.secondaryFormationLabel ? { label: 'Also Used', value: cfg.secondaryFormationLabel } : null,
      captain ? { label: 'Captain', value: captain.name } : null,
      gkStarter ? { label: 'First-Choice GK', value: players[gkStarter.slug].name } : null,
      stStarter ? { label: 'Primary Striker', value: players[stStarter.slug].name } : null,
      { label: 'Season', value: (cfg.season || data.season) + ' · ' + (cfg.competition || data.competition) },
    ].filter(Boolean);

    facts.forEach(function (f) {
      var cell = el('div', 'tac-summary-stat');
      cell.appendChild(el('div', 'tac-summary-value', esc(f.value)));
      cell.appendChild(el('div', 'tac-summary-label', esc(f.label)));
      root.appendChild(cell);
    });
  }

  /* ── Formation pitch ───────────────────────────────────────────────── */
  function renderPitch(root, cfg, players) {
    root.innerHTML = '';
    cfg.starters.forEach(function (s) {
      var p = players[s.slug];
      if (!p) return;
      var marker = el('a', 'formation-marker');
      marker.href = playerHref(p);
      marker.style.left = s.x + '%';
      marker.style.top = s.y + '%';
      marker.setAttribute('aria-label', p.name + ', ' + s.slot + ', OVR ' + p.ovr);

      marker.appendChild(byPhoto('formation-player-photo', p, true));
      var label = el('div', 'formation-player-label');
      label.appendChild(el('span', 'formation-player-name', esc(p.name.split(' ').slice(-1)[0])));
      label.appendChild(el('span', 'formation-player-meta', esc(s.slot) + ' &middot; ' + p.ovr));
      marker.appendChild(label);

      root.appendChild(marker);
    });
  }

  /* ── Preferred XI ───────────────────────────────────────────────────── */
  function renderPreferredXi(root, cfg, players) {
    root.innerHTML = '';
    BUCKET_ORDER.forEach(function (bucket) {
      var rows = cfg.starters.filter(function (s) { return SLOT_BUCKET[s.slot] === bucket; });
      if (!rows.length) return;
      var col = el('div', 'xi-col');
      col.appendChild(el('div', 'xi-col-head', bucket));
      rows.forEach(function (s) {
        var p = players[s.slug];
        if (!p) return;
        var row = el('a', 'xi-row');
        row.href = playerHref(p);
        row.appendChild(el('span', 'xi-slot', esc(s.slot)));
        row.appendChild(el('span', 'xi-name', esc(p.name)));
        row.appendChild(el('span', 'xi-ovr', p.ovr));
        col.appendChild(row);
      });
      root.appendChild(col);
    });
  }

  /* ── Positional Depth ──────────────────────────────────────────────── */
  function depthPlayerRow(entry, rank, players) {
    var p = players[entry.slug];
    if (!p) return null;
    var row = el('a', 'depth-player-row' + (p.loan ? ' is-loan' : ''));
    row.href = playerHref(p);

    row.appendChild(el('span', 'depth-player-rank', rank));
    row.appendChild(byPhoto('depth-player-photo', p, false));

    var body = el('div', 'depth-player-body');
    body.appendChild(el('span', 'depth-player-tier tier-' + entry.tier, TIER_LABEL[entry.tier] || entry.tier));
    body.appendChild(el('div', 'depth-player-name', esc(p.name) + (p.captain ? ' <span class="depth-player-cap">C</span>' : '')));
    var subBits = [esc(p.positions.join(' / ')), p.age + ' yrs'];
    if (p.loan) subBits.push('On loan: ' + esc(p.loan.club));
    body.appendChild(el('div', 'depth-player-sub', subBits.join(' &middot; ')));
    row.appendChild(body);

    var right = el('div', 'depth-player-right');
    if (p.group === 'Goalkeepers' && p.season) {
      right.appendChild(el('span', 'depth-player-ovr', p.ovr));
      if (p.season.trackedApps) {
        right.appendChild(el('span', 'depth-player-sub2', p.season.cleanSheets + ' CS / ' + p.season.trackedApps + ' tracked'));
      }
    } else {
      right.appendChild(el('span', 'depth-player-ovr', p.ovr));
    }
    row.appendChild(right);

    return row;
  }

  function renderPositionalDepth(root, cfg, players) {
    root.innerHTML = '';
    POSITION_GROUP_ORDER.forEach(function (groupName) {
      var entries = cfg.positionalDepth[groupName];
      if (!entries || !entries.length) return;

      var card = el('div', 'depth-position');
      var head = el('div', 'depth-position-head');
      head.appendChild(el('h3', null, groupName));
      var available = entries.filter(function (e) { return players[e.slug] && !players[e.slug].loan; }).length;
      head.appendChild(el('span', 'depth-position-count', available + ' available' + (entries.length > available ? ' (' + (entries.length - available) + ' on loan)' : '')));
      card.appendChild(head);

      var list = el('div', 'depth-position-list');
      entries.forEach(function (entry, i) {
        var row = depthPlayerRow(entry, i + 1, players);
        if (row) list.appendChild(row);
      });
      card.appendChild(list);
      root.appendChild(card);
    });
  }

  /* ── Tactical Flexibility ──────────────────────────────────────────── */
  function renderFlexibility(root, data) {
    var senior = data.players.filter(function (p) { return !p.loan; });
    var multi = senior.filter(function (p) { return p.positions.length >= 2; })
      .sort(function (a, b) { return b.positions.length - a.positions.length || a.name.localeCompare(b.name); });

    root.innerHTML = '';
    var summary = el('div', 'tac-flex-summary');
    summary.appendChild(el('span', 'tac-flex-count', multi.length));
    summary.appendChild(el('span', 'tac-flex-count-label', 'of ' + senior.length + ' senior players cover 2+ positions'));
    root.appendChild(summary);

    var list = el('div', 'tac-flex-list');
    multi.slice(0, 10).forEach(function (p) {
      var row = el('a', 'tac-flex-row');
      row.href = playerHref(p);
      row.appendChild(el('span', 'tac-flex-name', esc(p.name)));
      row.appendChild(el('span', 'tac-flex-positions', esc(p.positions.join(' / '))));
      list.appendChild(row);
    });
    root.appendChild(list);
  }

  /* ── Depth Health + Pressure Points ───────────────────────────────── */
  function renderDepthHealth(healthRoot, pressureRoot, cfg, players) {
    healthRoot.innerHTML = '';
    pressureRoot.innerHTML = '';
    var maxCount = 0;
    var counts = POSITION_GROUP_ORDER.map(function (groupName) {
      var entries = cfg.positionalDepth[groupName] || [];
      var available = entries.filter(function (e) { return players[e.slug] && !players[e.slug].loan; }).length;
      maxCount = Math.max(maxCount, available);
      return { groupName: groupName, available: available };
    });

    counts.forEach(function (c) {
      var row = el('div', 'depth-health-row');
      row.appendChild(el('span', 'depth-health-label', c.groupName));
      var bar = el('div', 'depth-health-bar');
      var fill = el('div', 'depth-health-fill');
      fill.style.width = (maxCount ? (c.available / maxCount * 100) : 0) + '%';
      if (c.available <= 1) fill.classList.add('is-thin');
      bar.appendChild(fill);
      row.appendChild(bar);
      row.appendChild(el('span', 'depth-health-count', c.available));
      healthRoot.appendChild(row);
    });

    var thin = counts.filter(function (c) { return c.available <= 1; });
    if (!thin.length) {
      pressureRoot.parentElement.style.display = 'none';
      return;
    }
    thin.forEach(function (c) {
      var row = el('div', 'pressure-point');
      row.appendChild(el('span', 'pressure-point-pos', c.groupName.toUpperCase()));
      row.appendChild(el('span', 'pressure-point-detail', c.available + ' natural option' + (c.available === 1 ? '' : 's')));
      pressureRoot.appendChild(row);
    });
  }

  /* ── Tactical Leaders ──────────────────────────────────────────────── */
  function renderLeaders(root, data, cfg, players) {
    root.innerHTML = '';
    var captain = data.players.find(function (p) { return p.captain; });
    var gkStarter = cfg.starters.find(function (s) { return s.slot === 'GK'; });
    var senior = data.players.filter(function (p) { return !p.loan; });
    var mostVersatile = senior.slice().sort(function (a, b) {
      return b.positions.length - a.positions.length || a.name.localeCompare(b.name);
    })[0];

    var leaders = [
      captain ? { label: 'Captain', p: captain } : null,
      gkStarter ? { label: 'First-Choice Goalkeeper', p: players[gkStarter.slug] } : null,
      mostVersatile && mostVersatile.positions.length >= 2
        ? { label: 'Most Versatile', p: mostVersatile, detail: mostVersatile.positions.join(' / ') }
        : null,
    ].filter(Boolean);

    leaders.forEach(function (l) {
      var card = el('a', 'tac-leader-card');
      card.href = playerHref(l.p);
      card.appendChild(byPhoto('tac-leader-photo', l.p, false));
      var body = el('div', 'tac-leader-body');
      body.appendChild(el('span', 'tac-leader-label', l.label));
      body.appendChild(el('div', 'tac-leader-name', esc(l.p.name)));
      body.appendChild(el('div', 'tac-leader-meta', esc(l.detail || l.p.positions.join(' / '))));
      card.appendChild(body);
      root.appendChild(card);
    });
  }

  /* ── Squad Notes ────────────────────────────────────────────────────── */
  function renderSquadNotes(root, cfg) {
    root.innerHTML = '';
    (cfg.squadNotes || []).forEach(function (note) {
      var item = el('div', 'squad-note');
      item.appendChild(el('div', 'squad-note-heading', esc(note.heading)));
      item.appendChild(el('div', 'squad-note-text', esc(note.text)));
      root.appendChild(item);
    });
  }

  /* ── Boot ───────────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    if (typeof SQUAD_DATA === 'undefined' || typeof TACTICAL_CONFIG === 'undefined') return;
    var data = SQUAD_DATA;
    var cfg = TACTICAL_CONFIG;
    var players = buildPlayerIndex(data);

    var contextEl = document.getElementById('tac-context');
    if (contextEl) contextEl.textContent = (cfg.season || data.season) + ' · ' + (cfg.competition || data.competition);

    var formationLabelEl = document.getElementById('tac-formation-label');
    if (formationLabelEl) formationLabelEl.textContent = cfg.formation.label + ' — Preferred XI';

    var summaryRoot = document.getElementById('tac-summary');
    if (summaryRoot) renderSummary(summaryRoot, data, cfg, players);

    var pitchRoot = document.getElementById('tac-pitch');
    if (pitchRoot) renderPitch(pitchRoot, cfg, players);

    var xiRoot = document.getElementById('tac-xi');
    if (xiRoot) renderPreferredXi(xiRoot, cfg, players);

    var depthRoot = document.getElementById('tac-depth');
    if (depthRoot) renderPositionalDepth(depthRoot, cfg, players);

    var flexRoot = document.getElementById('tac-flex');
    if (flexRoot) renderFlexibility(flexRoot, data);

    var healthRoot = document.getElementById('tac-health');
    var pressureRoot = document.getElementById('tac-pressure');
    if (healthRoot && pressureRoot) renderDepthHealth(healthRoot, pressureRoot, cfg, players);

    var leadersRoot = document.getElementById('tac-leaders');
    if (leadersRoot) renderLeaders(leadersRoot, data, cfg, players);

    var notesRoot = document.getElementById('tac-notes');
    if (notesRoot) renderSquadNotes(notesRoot, cfg);
  });
})();
