/* ─────────────────────────────────────────────────────────────────────────
   media.js — rendering for docs/media/index.html (the Media Centre / newsroom
   front page).

   Reads, and never invents:
     MEDIA_INDEX  assets/media_index.js  (scripts/generate_media_pages.py)

   Plain classic script, no modules, no fetch — index.html must keep working
   when opened straight off disk as a file:// page. Mirrors the pattern
   docs/assets/home.js uses for docs/index.html.
   ───────────────────────────────────────────────────────────────────────── */
(function () {
  'use strict';

  if (typeof MEDIA_INDEX === 'undefined') return;

  function esc(s) {
    return String(s === null || s === undefined ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function el(id) { return document.getElementById(id); }
  function set(id, html) { var n = el(id); if (n) n.innerHTML = html; }

  function person(authorId) { return MEDIA_INDEX.people[authorId] || null; }

  function initials(name) {
    return (name || '').trim().split(/\s+/).slice(0, 2).map(function (w) { return w.charAt(0); }).join('').toUpperCase();
  }

  /* Avatar markup: real headshot when we have one, otherwise an
     initials-on-accent-color circle — the same graceful fallback the
     generator uses server-side, so Press Corps cards never break for a
     journalist without a portrait asset. */
  function avatar(p, imgCls, monoCls) {
    if (!p) return '';
    if (p.headshot) return '<img class="' + imgCls + '" src="../' + esc(p.headshot) + '" alt="' + esc(p.name) + '">';
    return '<div class="' + monoCls + '" style="background:' + esc(p.accent_color || 'var(--steel)') + '">' + esc(initials(p.name)) + '</div>';
  }

  function kicker(a) {
    var p = person(a.author_id);
    if (p && p.is_press === false) return "The Hawk's Nest";
    if (a.content_type === 'dispatch') return 'The Red Dragon Dispatch';
    return a.outlet || a.category_label || 'Coverage';
  }

  function allArticles() {
    var out = [];
    for (var id in MEDIA_INDEX.articles) if (MEDIA_INDEX.articles.hasOwnProperty(id)) out.push(MEDIA_INDEX.articles[id]);
    return out;
  }

  function newsroomArticles() {
    // Everything that belongs in the newsroom feed — press coverage plus
    // Owen's match-day Dispatch. Jenkins' diary is deliberately excluded;
    // it gets its own Hawk's Nest section, never mixed into the wire feed.
    return allArticles().filter(function (a) { return a.content_type !== 'diary'; })
      .sort(function (x, y) { return y.date < x.date ? -1 : y.date > x.date ? 1 : 0; });
  }

  function url(a) {
    // MEDIA_INDEX urls are relative to docs/; this page already lives in
    // docs/media/, so an article URL (media/articles/x.html) just needs the
    // "media/" prefix stripped, while a journal URL (journal.html#x) needs
    // "../" prepended.
    if (a.url.indexOf('media/') === 0) return a.url.slice('media/'.length);
    return '../' + a.url;
  }

  /* ── Lead + supporting ─────────────────────────────────────────────── */
  function renderLead() {
    var pool = newsroomArticles();
    if (!pool.length) return;

    // Automatic pick — no per-session curation needed, so a brand new
    // article is compatible with the redesign the moment it's generated.
    // Prefer an explicitly `featured` article, else the most recent
    // "premium" (non-dispatch) piece, else fall back to the latest dispatch.
    var featured = pool.filter(function (a) { return a.featured; });
    var premium = pool.filter(function (a) { return a.content_type !== 'dispatch'; });
    var lead = featured[0] || premium[0] || pool[0];
    var rest = pool.filter(function (a) { return a.id !== lead.id; });
    var supporting = (premium.length > 1 ? premium.filter(function (a) { return a.id !== lead.id; }) : rest).slice(0, 3);
    if (supporting.length < 3) {
      rest.forEach(function (a) {
        if (supporting.length >= 3) return;
        if (supporting.indexOf(a) === -1 && a.id !== lead.id) supporting.push(a);
      });
    }

    var lp = person(lead.author_id);
    var leadImg = lead.image || 'assets/photos/wrexham-crest.png';
    var leadHtml = '<a class="mc-lead-link" href="' + esc(url(lead)) + '">' +
      '<div class="mc-lead-media"><img src="../' + esc(leadImg) + '" alt="' + esc(lead.image_alt || lead.headline) + '"></div>' +
      '<div class="mc-lead-copy">' +
      '<span class="mc-kicker">' + esc(kicker(lead)) + '</span>' +
      '<h2 class="mc-lead-title">' + esc(lead.headline) + '</h2>' +
      '<p class="mc-lead-deck">' + esc(lead.dek) + '</p>' +
      '<div class="mc-byline">' + avatar(lp, 'mc-byline-face', 'mc-byline-face-mono') +
      '<span><span class="mc-byline-name">' + esc(lp ? lp.name : '') + '</span><br>' +
      '<span class="mc-byline-date">' + esc(lead.date_label) + '</span></span></div>' +
      '</div></a>';

    var supportHtml = supporting.map(function (a) {
      var sp = person(a.author_id);
      var img = a.image;
      return '<a class="mc-support-row" href="' + esc(url(a)) + '">' +
        (img ? '<div class="mc-support-media"><img src="../' + esc(img) + '" alt="' + esc(a.image_alt || a.headline) + '" loading="lazy"></div>' : '') +
        '<div class="mc-support-copy">' +
        '<span class="mc-kicker" style="font-size:11px;margin-bottom:4px;">' + esc(kicker(a)) + '</span>' +
        '<h3 class="mc-support-title">' + esc(a.headline) + '</h3>' +
        '<span class="mc-support-meta">' + esc(sp ? sp.name : '') + ' &middot; ' + esc(a.date_label) + '</span>' +
        '</div></a>';
    }).join('');

    set('mc-lead-grid', leadHtml + '<div class="mc-supporting">' + supportHtml + '</div>');
  }

  /* ── Coverage categories ───────────────────────────────────────────── */
  function renderCategories() {
    var cats = MEDIA_INDEX.categories || [];
    var html = cats.map(function (c) {
      return '<a class="mc-cat-card" href="archive.html?category=' + esc(c.slug) + '">' +
        '<span class="mc-cat-card-label">' + esc(c.label) + '</span>' +
        '<span class="mc-cat-card-count">' + c.count + (c.count === 1 ? ' story' : ' stories') + '</span></a>';
    }).join('');
    set('mc-cat-grid', html);
  }

  /* ── Latest From the Newsroom (filterable wire feed) ─────────────────── */
  var FEED_LIMIT = 24;

  /* Three visual treatments, assigned deterministically from data already on
     hand (image presence + position) — never a per-article hardcoded flag.
     Exactly one row becomes "major" (the first story carrying a curated
     image); every other image-bearing story is "standard"; anything with no
     curated image falls back to the compact "wire" treatment, letting
     typography carry the row instead of a stretched-thumbnail placeholder. */
  function feedRow(a, idx, majorState) {
    var sp = person(a.author_id);
    var img = a.image;
    var tier = 'standard';
    if (!img) {
      tier = 'wire';
    } else if (!majorState.used) {
      tier = 'major';
      majorState.used = true;
    }
    var cls = 'mc-feed-item is-' + tier + (img ? '' : ' no-media');
    return '<a class="' + cls + '" href="' + esc(url(a)) + '" data-category="' + esc(a.category) + '">' +
      (img ? '<div class="mc-feed-media"><img src="../' + esc(img) + '" alt="' + esc(a.image_alt || a.headline) + '" loading="' + (idx < 3 ? 'eager' : 'lazy') + '"></div>' : '') +
      '<div class="mc-feed-copy">' +
      '<span class="mc-feed-kicker">' + esc(kicker(a)) + '</span>' +
      '<h3 class="mc-feed-title">' + esc(a.headline) + '</h3>' +
      (a.dek ? '<p class="mc-feed-dek">' + esc(a.dek) + '</p>' : '') +
      '<span class="mc-feed-meta">' + esc(sp ? sp.name : '') + ' &middot; ' + esc(a.date_label) + '</span>' +
      '</div></a>';
  }

  function renderFeed() {
    var pool = newsroomArticles().slice(0, FEED_LIMIT);
    var majorState = { used: false };
    set('mc-feed', pool.map(function (a, idx) { return feedRow(a, idx, majorState); }).join(''));

    var cats = MEDIA_INDEX.categories || [];
    var btns = ['<button type="button" class="mc-filter-btn is-active" data-value="all" aria-pressed="true">All</button>'];
    cats.forEach(function (c) {
      btns.push('<button type="button" class="mc-filter-btn" data-value="' + esc(c.slug) + '" aria-pressed="false">' + esc(c.label) + '</button>');
    });
    set('mc-filter-bar', btns.join(''));

    var barBtns = Array.prototype.slice.call(document.querySelectorAll('#mc-filter-bar .mc-filter-btn'));
    var items = Array.prototype.slice.call(document.querySelectorAll('#mc-feed .mc-feed-item'));
    barBtns.forEach(function (b) {
      b.addEventListener('click', function () {
        barBtns.forEach(function (x) { x.classList.remove('is-active'); x.setAttribute('aria-pressed', 'false'); });
        b.classList.add('is-active');
        b.setAttribute('aria-pressed', 'true');
        var val = b.dataset.value;
        items.forEach(function (it) {
          it.style.display = (val === 'all' || it.dataset.category === val) ? '' : 'none';
        });
      });
    });
  }

  /* ── The Press Corps ─────────────────────────────────────────────────── */
  function renderPressCorps() {
    var counts = {};
    allArticles().forEach(function (a) { counts[a.author_id] = (counts[a.author_id] || 0) + 1; });

    var cards = (MEDIA_INDEX.people_order || []).filter(function (id) {
      return MEDIA_INDEX.people[id].is_press;
    }).map(function (id) {
      var p = MEDIA_INDEX.people[id];
      var n = counts[id] || 0;
      return '<a class="press-card" href="archive.html?author=' + esc(id) + '" style="border-top-color:' + esc(p.accent_color || 'var(--steel)') + '">' +
        '<div class="press-card-top">' + avatar(p, 'press-avatar', 'press-avatar-mono') +
        '<div><div class="press-card-name">' + esc(p.name) + '</div>' +
        '<div class="press-card-role">' + esc(p.role) + ' &middot; ' + esc(p.outlet) + '</div></div></div>' +
        (p.bio ? '<p class="press-card-bio">' + esc(p.bio) + '</p>' : '') +
        '<div class="press-card-foot"><span class="press-card-count"><strong>' + n + '</strong> ' + (n === 1 ? 'article' : 'articles') + '</span>' +
        '<span class="press-card-cta">View coverage &rarr;</span></div></a>';
    }).join('');
    set('press-corps-grid', cards);
  }

  /* ── The Hawk's Nest ─────────────────────────────────────────────────── */
  function renderHawksNest() {
    var entries = allArticles().filter(function (a) { return a.content_type === 'diary'; })
      .sort(function (x, y) { return y.date < x.date ? -1 : y.date > x.date ? 1 : 0; })
      .slice(0, 3);
    if (!entries.length) { set('hawk-entries', '<p class="mc-empty">No journal entries yet.</p>'); return; }
    var html = entries.map(function (a) {
      return '<a class="hawk-entry" href="' + esc(url(a)) + '">' +
        (a.entry_number ? '<span class="hawk-entry-num">' + esc(a.entry_number) + '</span>' : '') +
        '<h3 class="hawk-entry-title">' + esc(a.headline) + '</h3>' +
        (a.dek ? '<p class="hawk-entry-dek">' + esc(a.dek) + '</p>' : '') +
        '<span class="hawk-entry-date">' + esc(a.date_label) + '</span></a>';
    }).join('');
    set('hawk-entries', html);
  }

  /* ── Voices Across Football ──────────────────────────────────────────── */
  function renderPublications() {
    var pubs = MEDIA_INDEX.publications || [];
    if (!pubs.length) { set('mc-pub-grid', '<p class="mc-empty">No press coverage yet.</p>'); return; }
    var html = pubs.map(function (pub) {
      var latest = MEDIA_INDEX.articles[pub.latest_id];
      return '<div class="mc-pub-card">' +
        '<div class="mc-pub-name">' + esc(pub.name) + '</div>' +
        '<div class="mc-pub-count">' + pub.count + (pub.count === 1 ? ' story' : ' stories') + '</div>' +
        (latest ? '<a class="mc-pub-latest" href="' + esc(url(latest)) + '">Latest: ' + esc(latest.headline) + '</a>' : '') +
        '</div>';
    }).join('');
    set('mc-pub-grid', html);
  }

  /* ── Media Archive teaser ────────────────────────────────────────────── */
  function renderArchiveTeaser() {
    var seasons = MEDIA_INDEX.seasons || [];
    if (!seasons.length) return;
    var html = seasons.map(function (s, i) {
      return '<a class="mc-archive-chip" href="archive.html?season=' + esc(s) + '">' + esc(s) +
        '<span>' + (i === 0 ? 'Current season' : 'Archived coverage') + '</span></a>';
    }).join('') + '<a class="mc-archive-chip" href="archive.html">Everything<span>Full archive</span></a>';
    set('mc-archive-teaser', html);
  }

  try { renderLead(); } catch (e) { }
  try { renderCategories(); } catch (e) { }
  try { renderFeed(); } catch (e) { }
  try { renderPressCorps(); } catch (e) { }
  try { renderHawksNest(); } catch (e) { }
  try { renderPublications(); } catch (e) { }
  try { renderArchiveTeaser(); } catch (e) { }
})();
