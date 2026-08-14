/* ─────────────────────────────────────────────────────────────────────────
   home.js — rendering for docs/index.html (THE JENKINS ERA homepage).

   Reads, and never invents:
     SEASON_SUMMARY        inline in index.html   (scripts/sync_season_summary.py)
     MEDIA_INDEX           assets/media_index.js  (scripts/generate_media_pages.py)
     PREMIER_LEAGUE_TABLE  assets/pl_table.js     (hand-maintained standings)
     PLAYER_SEASON_STATS   assets/player_stats.js (scripts/sync_home_player_stats.py)
     HOME_CONFIG           assets/home_config.js  (editorial choices only)

   Plain classic script, no modules, no fetch — index.html must keep working
   when opened straight off disk as a file:// page.
   ───────────────────────────────────────────────────────────────────────── */
(function () {
  'use strict';

  var EPL = 'assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/';
  var EFC = 'assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/';

  var OPPONENT_CRESTS = {
    'Arsenal': EPL + 'arsenal.football-logos.cc.png',
    'Aston Villa': EPL + 'aston-villa.football-logos.cc.png',
    'Bournemouth': EPL + 'bournemouth.football-logos.cc.png',
    'Brentford': EPL + 'brentford.football-logos.cc.png',
    'Brighton': EPL + 'brighton.football-logos.cc.png',
    'Chelsea': EPL + 'chelsea.football-logos.cc.png',
    'Crystal Palace': EPL + 'crystal-palace.football-logos.cc.png',
    'Ipswich Town': EPL + 'ipswich.football-logos.cc.png',
    'Leeds United': EPL + 'leeds-united.football-logos.cc.png',
    'Liverpool': EPL + 'liverpool.football-logos.cc.png',
    'Manchester City': EPL + 'manchester-city.football-logos.cc.png',
    'Manchester United': EPL + 'manchester-united.football-logos.cc.png',
    'Newcastle': EPL + 'newcastle.football-logos.cc.png',
    'Nottingham Forest': EPL + 'nottingham-forest.football-logos.cc.png',
    'Sunderland': EPL + 'sunderland.football-logos.cc.png',
    'Tottenham': EPL + 'tottenham.football-logos.cc.png',
    'Sheffield United': EFC + 'sheffield-united.football-logos.cc.png',
    'West Ham': EFC + 'west-ham.football-logos.cc.png',
    'Wolves': EFC + 'wolves.football-logos.cc.png',
    'Blackburn Rovers': 'assets/photos/crests/blackburn-rovers.png'
  };

  var COMP_LOGOS = {
    'Premier League': 'assets/photos/premier-league-england-white-logo-footylogos.png',
    'EFL Championship': 'assets/photos/efl-championship-england-logo-footylogos.png',
    'Carabao Cup': 'assets/photos/carabao-cup.png',
    'FA Cup': 'assets/photos/crests/england_emirates-fa-cup_512x512.football-logos.cc.png'
  };

  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function esc(s) {
    return String(s === null || s === undefined ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function fmtDate(iso) {
    if (!iso) return '';
    var p = iso.split('-');
    return MONTHS[parseInt(p[1], 10) - 1] + ' ' + parseInt(p[2], 10) + ', ' + p[0];
  }

  function el(id) { return document.getElementById(id); }

  function set(id, html) {
    var node = el(id);
    if (node) node.innerHTML = html;
  }

  function article(id) {
    return (typeof MEDIA_INDEX !== 'undefined' && MEDIA_INDEX.articles) ? MEDIA_INDEX.articles[id] : null;
  }

  function person(authorId) {
    return (typeof MEDIA_INDEX !== 'undefined' && MEDIA_INDEX.people) ? MEDIA_INDEX.people[authorId] : null;
  }

  /* Category label for an article: prefer the outlet for press pieces, the
     stored section otherwise. Nothing invented — both come from the JSON. */
  function kicker(a) {
    var p = person(a.author_id);
    if (p && !p.is_press) return "The Hawk's Nest";
    if (a.content_type === 'dispatch') return 'The Red Dragon Dispatch';
    return a.outlet || (a.section || 'Feature');
  }

  /* ── 1. Editorial hero ─────────────────────────────────────────────── */
  function renderHero() {
    var cfg = HOME_CONFIG.lead;
    var a = article(cfg.articleId);
    if (!a) return;
    var p = person(a.author_id) || {};

    var byline = '<span class="home-byline-name">' + esc(p.name || '') + '</span>' +
      (p.role ? '<span class="home-byline-role">' + esc(p.role) + ' &middot; ' + esc(a.outlet) + '</span>' : '');

    set('home-hero-lead',
      '<a class="home-hero-link" href="' + esc(a.url) + '">' +
      '  <div class="home-hero-media">' +
      '    <img src="' + esc(cfg.image) + '" alt="' + esc(cfg.imageAlt) + '">' +
      '    <div class="home-hero-overlay"></div>' +
      '  </div>' +
      '  <div class="home-hero-copy">' +
      '    <span class="home-hero-kicker">' + esc(kicker(a)) + '</span>' +
      '    <h2 class="home-hero-title">' + esc(a.headline) + '</h2>' +
      '    <p class="home-hero-deck">' + esc(a.dek) + '</p>' +
      '    <div class="home-byline">' +
      (p.headshot ? '<img class="home-byline-face" src="' + esc(p.headshot) + '" alt="' + esc(p.name) + '">' : '') +
      '      <div class="home-byline-text">' + byline + '</div>' +
      '      <span class="home-byline-date">' + esc(a.date_label) + '</span>' +
      '    </div>' +
      '  </div>' +
      '</a>');

    var rows = HOME_CONFIG.supporting.map(function (item) {
      var s = article(item.articleId);
      if (!s) return '';
      var sp = person(s.author_id) || {};
      return '<a class="home-story-row" href="' + esc(s.url) + '">' +
        '<div class="home-story-media"><img src="' + esc(item.image) + '" alt="' + esc(item.imageAlt) + '"></div>' +
        '<div class="home-story-copy">' +
        '<span class="home-story-kicker">' + esc(kicker(s)) + '</span>' +
        '<h3 class="home-story-title">' + esc(s.headline) + '</h3>' +
        '<span class="home-story-meta">' + esc(sp.name || '') + ' &middot; ' + esc(s.date_label) + '</span>' +
        '</div></a>';
    }).join('');
    set('home-supporting-stories', rows);
  }

  /* ── 2. Match pulse ────────────────────────────────────────────────── */
  function crestImg(name, cls) {
    var src = OPPONENT_CRESTS[name];
    return src ? '<img class="' + cls + '" src="' + esc(src) + '" alt="">' : '';
  }

  function renderPulse() {
    var s = (typeof SEASON_SUMMARY !== 'undefined') ? SEASON_SUMMARY : null;
    if (!s) return;

    var latest = s.latest;
    if (latest) {
      var comp = COMP_LOGOS[latest.competition];
      set('home-result',
        '<div class="home-pulse-label">Latest Result</div>' +
        '<div class="home-result-comp">' +
        (comp ? '<img src="' + esc(comp) + '" alt="">' : '') + esc(latest.competition) + '</div>' +
        '<div class="home-result-line">' +
        '<img class="home-result-crest" src="assets/photos/crests/wrexham-crest.png" alt="Wrexham">' +
        '<span class="home-result-score ' + (latest.result === 'W' ? 'is-win' : latest.result === 'L' ? 'is-loss' : 'is-draw') + '">' +
        esc(latest.score) + '</span>' +
        crestImg(latest.opponent, 'home-result-crest') +
        '</div>' +
        '<div class="home-result-meta">' + (latest.home ? 'Home' : 'Away') + ' v ' + esc(latest.opponent) +
        ' &middot; ' + esc(fmtDate(latest.date)) + '</div>');
    }

    var next = null;
    (s.schedule || []).some(function (fx) {
      if (!fx.result) { next = fx; return true; }
      return false;
    });
    if (next) {
      var nextComp = (s._meta || {}).competition;
      var nextCompLogo = COMP_LOGOS[nextComp];
      set('home-next-match',
        '<div class="home-pulse-label">Next Match</div>' +
        (nextComp ?
          '<div class="home-result-comp">' +
          (nextCompLogo ? '<img src="' + esc(nextCompLogo) + '" alt="">' : '') + esc(nextComp) + '</div>'
          : '') +
        '<div class="home-next-line">' +
        crestImg(next.opponent, 'home-next-crest') +
        '<span class="home-next-opponent">' + esc(next.opponent) + '</span>' +
        '</div>' +
        '<div class="home-result-meta">' + (next.home ? 'Home' : 'Away') +
        ' &middot; Matchday ' + esc(next.md) + ' &middot; ' + esc(fmtDate(next.date)) + '</div>');
    }

    var form = s.form || [];
    if (form.length) {
      var pips = form.map(function (m) {
        var cls = m.result === 'W' ? 'is-win' : m.result === 'L' ? 'is-loss' : 'is-draw';
        var title = (m.home ? 'v ' : 'at ') + m.opponent + ' ' + m.score + ' · ' + m.competition + ' · ' + fmtDate(m.date);
        return '<span class="home-form-pip ' + cls + '" title="' + esc(title) + '">' + esc(m.result) + '</span>';
      }).join('');
      set('home-form',
        '<div class="home-pulse-label">Form &middot; Last 5</div>' +
        '<div class="home-form-pips">' + pips + '</div>' +
        '<div class="home-result-meta">First-team competitive matches</div>');
    }

    var wrx = wrexhamRow();
    if (wrx) {
      set('home-current-position',
        '<div class="home-pulse-label">Premier League</div>' +
        '<div class="home-standing-grid">' +
        '<div><span class="home-standing-num">' + esc(ordinal(wrx.pos)) + '</span><span class="home-standing-key">Position</span></div>' +
        '<div><span class="home-standing-num">' + esc(wrx.pts) + '</span><span class="home-standing-key">Points</span></div>' +
        '<div><span class="home-standing-num">' + (wrx.gd > 0 ? '+' : '') + esc(wrx.gd) + '</span><span class="home-standing-key">Goal Diff</span></div>' +
        '</div>' +
        '<div class="home-result-meta">' + esc(wrx.p) + ' played &middot; ' + esc(s._meta.season) + '</div>');
    }
  }

  function ordinal(n) {
    var v = n % 100;
    if (v >= 11 && v <= 13) return n + 'th';
    return n + (['th', 'st', 'nd', 'rd'][n % 10] || 'th');
  }

  function wrexhamRow() {
    if (typeof PREMIER_LEAGUE_TABLE === 'undefined') return null;
    for (var i = 0; i < PREMIER_LEAGUE_TABLE.rows.length; i++) {
      if (PREMIER_LEAGUE_TABLE.rows[i].wrexham) return PREMIER_LEAGUE_TABLE.rows[i];
    }
    return null;
  }

  /* ── 3. Title race + full tables ───────────────────────────────────── */
  function renderTitleRace() {
    if (typeof PREMIER_LEAGUE_TABLE === 'undefined') return;
    var rows = PREMIER_LEAGUE_TABLE.rows;
    var wrxIdx = -1;
    rows.forEach(function (r, i) { if (r.wrexham) wrxIdx = i; });

    /* Top four, plus Wrexham and its immediate neighbours if it sits lower. */
    var keep = {};
    for (var i = 0; i < Math.min(4, rows.length); i++) keep[i] = true;
    if (wrxIdx > -1) {
      [wrxIdx - 1, wrxIdx, wrxIdx + 1].forEach(function (i) {
        if (i >= 0 && i < rows.length) keep[i] = true;
      });
    }
    var picked = Object.keys(keep).map(Number).sort(function (a, b) { return a - b; });

    var html = '';
    var prev = null;
    picked.forEach(function (i) {
      var r = rows[i];
      if (prev !== null && r.pos !== prev + 1) {
        html += '<tr class="home-race-break"><td colspan="5">&middot; &middot; &middot;</td></tr>';
      }
      html += '<tr class="' + (r.wrexham ? 'home-race-wrexham' : '') + '">' +
        '<td class="home-race-pos">' + esc(r.pos) + '</td>' +
        '<td class="home-race-club">' +
        (r.crest ? '<img src="' + esc(r.crest) + '" alt="">' : '') + esc(r.club) + '</td>' +
        '<td>' + esc(r.p) + '</td>' +
        '<td>' + (r.gd > 0 ? '+' : '') + esc(r.gd) + '</td>' +
        '<td class="home-race-pts">' + esc(r.pts) + '</td>' +
        '</tr>';
      prev = r.pos;
    });
    set('home-title-race-body', html);
  }

  function renderFullTable(target, table) {
    var node = el(target);
    if (!node || typeof table === 'undefined') return;
    var html = '';
    table.rows.forEach(function (r) {
      var marker = table.markers[r.pos];
      if (marker) {
        html += '<tr class="table-gap gap-' + esc(marker.cls) + '"><td colspan="10">' + marker.label + '</td></tr>';
      }
      var cls = r.cls ? 'table-' + r.cls : '';
      if (r.wrexham) cls += ' wrexham-row';
      html += '<tr class="' + cls.trim() + '">' +
        '<td>' + esc(r.pos) + '</td>' +
        '<td><div class="st-club">' + (r.crest ? '<img class="st-crest" src="' + esc(r.crest) + '" alt="">' : '') +
        esc(r.club) + (r.wrexham ? ' ★' : '') + '</div></td>' +
        '<td>' + esc(r.p) + '</td><td>' + esc(r.w) + '</td><td>' + esc(r.d) + '</td><td>' + esc(r.l) + '</td>' +
        '<td>' + esc(r.gf) + '</td><td>' + esc(r.ga) + '</td>' +
        '<td>' + (r.gd > 0 ? '+' : '') + esc(r.gd) + '</td>' +
        '<td>' + esc(r.pts) + '</td></tr>';
    });
    node.innerHTML = html;
  }

  /* ── 4. From Our Writers ───────────────────────────────────────────── */
  function renderWriters() {
    var cards = HOME_CONFIG.writers.map(function (item) {
      var a = article(item.articleId);
      if (!a) return '';
      var p = person(a.author_id) || {};
      var hawk = p.is_press === false;
      return '<a class="writer-card' + (hawk ? ' writer-card-hawk' : '') + '" href="' + esc(a.url) + '"' +
        (p.accent_color && !hawk ? ' style="--writer-accent:' + esc(p.accent_color) + '"' : '') + '>' +
        '<div class="writer-card-media"><img src="' + esc(item.image) + '" alt="' + esc(item.imageAlt) + '"></div>' +
        '<div class="writer-card-body">' +
        '<span class="writer-card-outlet">' + esc(hawk ? "The Hawk's Nest" : a.outlet) + '</span>' +
        '<h3 class="writer-card-title">' + esc(hawk && a.entry_number ? a.dek : a.headline) + '</h3>' +
        '<div class="writer-card-byline">' +
        (p.headshot ? '<img class="writer-card-face" src="' + esc(p.headshot) + '" alt="">' : '<span class="writer-card-face writer-card-face-mono">KJ</span>') +
        '<span><strong>' + esc(p.name || '') + '</strong>' + esc(p.role ? ' · ' + p.role : '') + '</span>' +
        '<span class="writer-card-date">' + esc(hawk && a.entry_number ? a.entry_number + ' · ' + a.date_label : a.date_label) + '</span>' +
        '</div></div></a>';
    }).join('');
    set('writer-grid', cards);

    if (typeof MEDIA_INDEX === 'undefined' || !MEDIA_INDEX.people_order) return;
    var strip = MEDIA_INDEX.people_order.map(function (id) {
      var p = MEDIA_INDEX.people[id];
      if (!p.is_press) return '';
      return '<span class="press-corps-item">' +
        (p.headshot ? '<img src="' + esc(p.headshot) + '" alt="">' : '') +
        '<span><strong>' + esc(p.name) + '</strong>' + esc(p.outlet) + '</span></span>';
    }).join('');
    set('press-corps', strip);
  }

  /* ── 5. Squad + Academy ────────────────────────────────────────────── */
  function abbreviatedName(fullName) {
    var parts = (fullName || '').trim().split(/\s+/);
    if (parts.length < 2) return fullName;
    return parts[0].charAt(0) + '. ' + parts.slice(1).join(' ');
  }

  function seasonStatsFor(fullName) {
    if (typeof PLAYER_SEASON_STATS === 'undefined') return null;
    return PLAYER_SEASON_STATS[fullName] || PLAYER_SEASON_STATS[abbreviatedName(fullName)] || null;
  }

  function miniCards(list, cls) {
    return list.map(function (p) {
      return '<div class="player-mini-card">' +
        '<div class="player-mini-media"><img src="' + esc(p.image) + '" alt="' + esc(p.name) + '"></div>' +
        '<div class="player-mini-body">' +
        '<span class="player-mini-name">' + esc(p.name) + '</span>' +
        '<span class="player-mini-meta">' + esc(p.position) + ' &middot; ' + esc(p.age) + '</span>' +
        '</div>' +
        '<span class="player-mini-ovr' + (cls ? ' ' + cls : '') + '">' + esc(p.ovr) + '</span>' +
        '</div>';
    }).join('');
  }

  function renderSquad() {
    var f = HOME_CONFIG.spotlight.featured;
    var stats = seasonStatsFor(f.name);
    set('player-feature',
      '<div class="player-feature-media"><img src="' + esc(f.image) + '" alt="' + esc(f.name) + '"></div>' +
      '<div class="player-feature-body">' +
      '<span class="player-feature-kicker">Featured Player</span>' +
      '<h3 class="player-feature-name">' + esc(f.name) + '</h3>' +
      '<div class="player-feature-facts player-feature-facts-4">' +
      '<span><strong>' + esc(f.position) + '</strong>Position</span>' +
      '<span><strong>' + esc(f.age) + '</strong>Age</span>' +
      '<span><strong>' + esc(f.height) + '</strong>Height</span>' +
      '<span><strong>' + esc(f.ovr) + '</strong>OVR</span>' +
      '</div>' +
      (stats ?
        '<div class="player-feature-season">' +
        '<span class="player-feature-season-label">2026&ndash;27 Season</span>' +
        '<div class="player-feature-season-stats">' +
        '<span><strong>' + esc(stats.goals) + '</strong>Goals</span>' +
        '<span><strong>' + esc(stats.assists) + '</strong>Assists</span>' +
        '<span><strong>' + esc(stats.rating.toFixed(1)) + '</strong>Avg Rating</span>' +
        '</div></div>'
        : '') +
      '<p class="player-feature-note">Squad data from <code>wrexham_squad.csv</code>. ' +
      (stats ? 'Full season detail, including apps and MOTM awards, is on the '
             : 'Season appearances, goals and assists are kept on the ') +
      '<a href="season.html">season stats page</a>.</p>' +
      '</div>');
    set('player-mini-grid', miniCards(HOME_CONFIG.spotlight.others, ''));
  }

  function renderAcademy() {
    var f = HOME_CONFIG.academy.featured;
    set('academy-feature',
      '<div class="academy-feature-media"><img src="' + esc(f.image) + '" alt="' + esc(f.name) + '"></div>' +
      '<div class="academy-feature-body">' +
      '<span class="academy-feature-kicker">Prospect Watch</span>' +
      '<h3 class="academy-feature-name">' + esc(f.name) + '</h3>' +
      '<div class="player-feature-facts">' +
      '<span><strong>' + esc(f.position) + '</strong>Position</span>' +
      '<span><strong>' + esc(f.age) + '</strong>Age</span>' +
      '<span><strong>' + esc(f.nationality) + '</strong>Nationality</span>' +
      '<span><strong>' + esc(f.ovr) + '</strong>OVR</span>' +
      '<span><strong>' + esc(f.potential) + '</strong>Potential</span>' +
      '</div>' +
      '</div>');
    set('academy-mini-grid', HOME_CONFIG.academy.others.map(function (p) {
      return '<div class="player-mini-card">' +
        '<div class="player-mini-media"><img src="' + esc(p.image) + '" alt="' + esc(p.name) + '"></div>' +
        '<div class="player-mini-body">' +
        '<span class="player-mini-name">' + esc(p.name) + '</span>' +
        '<span class="player-mini-meta">' + esc(p.position) + ' &middot; ' + esc(p.age) + ' &middot; POT ' + esc(p.potential) + '</span>' +
        '</div>' +
        '<span class="player-mini-ovr is-academy">' + esc(p.ovr) + '</span>' +
        '</div>';
    }).join(''));
  }

  /* ── 6. Jenkins Era — current-season node ──────────────────────────── */
  function renderEraCurrent() {
    var s = (typeof SEASON_SUMMARY !== 'undefined') ? SEASON_SUMMARY : null;
    var wrx = wrexhamRow();
    if (!s || !wrx) return;
    set('era-current-detail',
      esc(ordinal(wrx.pos)) + ' in the Premier League after ' + esc(wrx.p) + ' matches &middot; ' +
      esc(wrx.pts) + ' points &middot; ' + esc(s.stats.played) + ' competitive matches played across all competitions.');
  }

  /* ── 7. Record room: full Premier League fixture list ──────────────── */
  function renderSchedule() {
    var s = (typeof SEASON_SUMMARY !== 'undefined') ? SEASON_SUMMARY : null;
    if (!s || !s.schedule) return;
    var html = s.schedule.map(function (fx) {
      var tag = fx.result
        ? '<span class="home-fx-tag ' + (fx.result === 'W' ? 'is-win' : fx.result === 'L' ? 'is-loss' : 'is-draw') + '">' +
        esc(fx.result) + ' ' + esc(fx.score) + '</span>'
        : '<span class="home-fx-tag">MD' + esc(fx.md) + '</span>';
      return '<div class="home-fx-row">' +
        '<span class="home-fx-club">' + crestImg(fx.opponent, 'home-fx-crest') +
        (fx.home ? 'v ' : 'at ') + esc(fx.opponent) + '</span>' +
        '<span class="home-fx-date">' + esc(fmtDate(fx.date)) + '</span>' + tag + '</div>';
    }).join('');
    set('home-fixture-list', html);
  }

  /* ── 8. From the archives (club heritage note) ─────────────────────── */
  /* Real Wrexham AFC history, carried over verbatim from the previous
     homepage. Nothing here is career-mode data. */
  function renderArchiveNote() {
    var onThisDay = {
      '10-04': { y: 1864, t: 'Wrexham AFC is founded at the Turf Hotel — the oldest football club in Wales.' },
      '01-04': { y: 1992, t: 'Wrexham 2–1 Arsenal: bottom of the Football League beat the reigning champions, Mickey Thomas with the free kick.' },
      '01-26': { y: 1957, t: 'A record 34,445 pack the Racecourse for an FA Cup tie with Manchester United.' },
      '03-03': { y: 1962, t: 'Wrexham record their biggest ever win, 10–1 against Hartlepools United.' },
      '03-05': { y: 1877, t: 'Wales play their first home international at the Racecourse — still the oldest international ground in use.' },
      '10-15': { y: 1963, t: "The club's heaviest defeat, 0–9 away at Brentford." },
      '09-01': { y: 2022, t: "Wrexham is granted city status in the Platinum Jubilee honours — Wales's seventh city." },
      '12-26': { y: 1936, t: 'A record league crowd of 29,261 watch Wrexham face Chester City.' }
    };
    var archive = [
      "Tommy Bamford's 51 goals in 1933–34 is still the club's single-season record.",
      'Arfon Griffiths — "Mr Wrexham" — made a record 592 league appearances.',
      'The 111 points won in 2022–23 is a record for the top five tiers of English football.',
      'Wrexham have won the Welsh Cup a record 23 times.',
      "The 1975–76 Cup Winners' Cup run reached the quarter-finals, beating FC Porto along the way.",
      'Wrexham spent 15 seasons in non-league (2008–2023) before three straight promotions.',
      'In 160+ years, Wrexham have never played in the English top flight — a first is in reach this season.',
      "The Racecourse has staged football since 1864 and is the world's oldest international stadium still in use."
    ];
    var now = new Date();
    var key = String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
    var labelEl = el('otd-label'), textEl = el('otd-text');
    if (!labelEl || !textEl) return;
    if (onThisDay[key]) {
      labelEl.textContent = 'On This Day · ' + onThisDay[key].y;
      textEl.textContent = onThisDay[key].t;
    } else {
      var doy = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
      labelEl.textContent = 'From the Archives';
      textEl.textContent = archive[doy % archive.length];
    }
  }

  /* ── Boot ──────────────────────────────────────────────────────────── */
  try { renderHero(); } catch (e) { }
  try { renderPulse(); } catch (e) { }
  try { renderTitleRace(); } catch (e) { }
  try { renderFullTable('home-full-table-body', PREMIER_LEAGUE_TABLE); } catch (e) { }
  try { renderFullTable('home-archive-table-body', CHAMPIONSHIP_2025_26_FINAL); } catch (e) { }
  try { renderWriters(); } catch (e) { }
  try { renderSquad(); } catch (e) { }
  try { renderAcademy(); } catch (e) { }
  try { renderEraCurrent(); } catch (e) { }
  try { renderSchedule(); } catch (e) { }
  try { renderArchiveNote(); } catch (e) { }
})();
