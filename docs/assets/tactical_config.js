/* tactical_config.js — the ONLY hand-curated part of the Tactical Centre.
   Same philosophy as home_config.js / squad_config.js: this file records
   Keeyvon Jenkins' managerial decisions (formation shape, pitch slot
   assignment, positional depth order/tier) that exist nowhere else in the
   repository — never a mutable stat. Every player is referenced by slug
   only; name, age, OVR, position list, photo, loan status and dossier URL
   are all joined in at render time from docs/assets/squad_data.js (the
   generated senior-squad data file already powering the Squad page).

   Depth order within each position is Jenkins' actual pecking order as
   tracked across the season (previously the ordering baked into
   docs/depth_chart.html's dc-subsection blocks) — NOT sorted by OVR.
   Tier is one of 'starter' | 'rotation' | 'prospect', reused verbatim from
   that prior curation (never invented labels beyond what was already
   tracked there). Loan status itself is not duplicated here — it's read
   from squad_data.js's `loan` field. */
const TACTICAL_CONFIG = {
  season: '2026/27',
  competition: 'Premier League',

  formation: {
    id: '4-3-3-cam',
    label: '4-3-3 (w/ CAM)',
  },
  // Jenkins' broader tactical identity also includes a 4-2-3-1, per his
  // Dossier's Tactical Identity pills — noted here as a fact, not built out
  // as a second switchable pitch, since no distinct stored starting XI for
  // it exists separately from the shape below.
  secondaryFormationLabel: '4-2-3-1',

  // Pitch slots for the current preferred XI. x/y are percentages of the
  // pitch surface (y: 0 = attacking/opposition end, 100 = own goal line).
  starters: [
    { slug: 'arthur-okonkwo',  slot: 'GK',  x: 50, y: 93 },
    { slug: 'jorthy-mokio',    slot: 'LB',  x: 14, y: 74 },
    { slug: 'callum-doyle',    slot: 'CB',  x: 37, y: 78 },
    { slug: 'ayden-heaven',    slot: 'CB',  x: 63, y: 78 },
    { slug: 'liberato-cacace', slot: 'RB',  x: 86, y: 74 },
    { slug: 'damian-bobadilla',slot: 'CM',  x: 30, y: 54 },
    { slug: 'brian-gutierrez', slot: 'CM',  x: 70, y: 54 },
    { slug: 'toni-fruk',       slot: 'CAM', x: 50, y: 38 },
    { slug: 'rio-ngumoha',     slot: 'LW',  x: 14, y: 16 },
    { slug: 'yacel-amrizi',    slot: 'ST',  x: 50, y: 8 },
    { slug: 'leo-sauer',       slot: 'RW',  x: 86, y: 16 },
  ],

  // Positional depth, Jenkins' pecking order. Position-group labels match
  // the taxonomy this squad's roles actually use (matches the prior
  // docs/depth_chart.html sections one-for-one).
  positionalDepth: {
    'Goalkeeper': [
      { slug: 'arthur-okonkwo',  tier: 'starter' },
      { slug: 'bernt-klaverboer',tier: 'rotation' },
      { slug: 'mason-webber',    tier: 'prospect' },
      { slug: 'nico-kopp',       tier: 'prospect' },
    ],
    'Left Back': [
      { slug: 'jorthy-mokio',  tier: 'starter' },
      { slug: 'jermaine-lord', tier: 'prospect' },
    ],
    'Right Back': [
      { slug: 'liberato-cacace', tier: 'starter' },
      { slug: 'joenathan-amelia',tier: 'rotation' },
      { slug: 'elijah-dijkstra', tier: 'rotation' },
      { slug: 'mario-barbieri',  tier: 'rotation' },
      { slug: 'aaron-james',     tier: 'prospect' },
    ],
    'Centre Back': [
      { slug: 'callum-doyle',    tier: 'starter' },
      { slug: 'ayden-heaven',    tier: 'starter' },
      { slug: 'max-cleworth',    tier: 'rotation' },
      { slug: 'aaron-james',     tier: 'prospect' },
      { slug: 'andres-cuenca',   tier: 'prospect' },
      { slug: 'vittorio-martini',tier: 'prospect' },
    ],
    'Defensive Midfield': [
      { slug: 'damian-bobadilla',tier: 'starter' },
      { slug: 'jorthy-mokio',    tier: 'rotation' },
      { slug: 'jamal-belghazi',  tier: 'prospect' },
      { slug: 'carlos-macia',    tier: 'prospect' },
      { slug: 'emiliano-bianchi',tier: 'prospect' },
    ],
    'Central Midfield': [
      { slug: 'damian-bobadilla',tier: 'starter' },
      { slug: 'toni-fruk',       tier: 'starter' },
      { slug: 'jorthy-mokio',    tier: 'rotation' },
      { slug: 'thiago-pitarch',  tier: 'rotation' },
      { slug: 'milan-vitalis',   tier: 'rotation' },
      { slug: 'carlos-macia',    tier: 'prospect' },
    ],
    'Attacking Midfield': [
      { slug: 'toni-fruk',        tier: 'starter' },
      { slug: 'brian-gutierrez',  tier: 'starter' },
      { slug: 'santiago-ortega',  tier: 'prospect' },
      { slug: 'juan-cruz-vargas', tier: 'prospect' },
      { slug: 'fabricio-sandoval',tier: 'prospect' },
    ],
    'Left Wing': [
      { slug: 'rio-ngumoha',     tier: 'starter' },
      { slug: 'leo-sauer',       tier: 'rotation' },
      { slug: 'yacel-amrizi',    tier: 'rotation' },
      { slug: 'santiago-ortega', tier: 'prospect' },
      { slug: 'marco-soria',     tier: 'prospect' },
    ],
    'Right Wing': [
      { slug: 'andres-gomez',      tier: 'starter' },
      { slug: 'vladyslav-veleten', tier: 'rotation' },
      { slug: 'lilian-faure',      tier: 'prospect' },
    ],
    'Striker': [
      { slug: 'toni-fruk',          tier: 'starter' },
      { slug: 'yacel-amrizi',       tier: 'starter' },
      { slug: 'chido-obi',          tier: 'rotation' },
      { slug: 'bailey-cadamarteri', tier: 'rotation' },
      { slug: 'alan-minda',         tier: 'rotation' },
      { slug: 'matthieu-brunel',    tier: 'prospect' },
    ],
  },

  // Squad-notes narrative retained from the prior Depth Chart's "Window
  // Priorities" tracking — factual transfer-window commentary, not
  // re-derived here. Kept verbatim in substance.
  squadNotes: [
    {
      heading: 'Central Midfield (U22) — Resolved',
      text: 'The club went through a long stretch with no under-20 central midfielder on the books, after H. Ashfield was sold to Silkeborg IF (Aug 2026) and the experienced CM cover (Sheaf, O’Brien, Rathbone) aged out without a young replacement. Damián Bobadilla (24, free signing, Feb 2026) added senior depth but didn’t solve the age gap. Carlos Macia (17, signed from Villarreal, deadline day 2026) was immediately loaned to Swansea City. Thiago Pitarch (19, signed from Real Madrid, Dec 2026) finally closed it — an under-20 CM actually in the matchday squad.',
    },
    {
      heading: 'Striker (U21)',
      text: 'Kieffer Moore (33) and Jay Rodriguez (36) have both departed, and Faal (23) was sold to Barracas Central. Toni Fruk (25, 79 OVR) is the club’s top-rated senior striker. Chido Obi (18, signed from Man Utd’s academy) is the high-ceiling young striker option, still raw and rotation-tier for now — senior depth behind Fruk and Amrizi is thinner than it’s been all season.',
    },
    {
      heading: 'Attacking Midfield (U21)',
      text: 'Windass’s sale to Wolves left a live creative gap. Santiago Ortega (18, promoted from academy) debuted with an assist but remains raw (63 OVR). Brian Gutiérrez (22, 73 OVR) is the senior option stepping into the gap in the meantime.',
    },
    {
      heading: 'Right Back — Resolved',
      text: 'Elijah Dijkstra (20, signed from Sunderland) gave Amelia genuine senior competition at RB for the first time since Kaboré’s loan ended without a permanent deal. Liberato Cacace’s transition from LB to RB (2026-08-15) has since made this the deepest position on the pitch — he now starts ahead of Amelia, Dijkstra and Barbieri.',
    },
    {
      heading: 'Left Back — Open Gap',
      text: 'Cacace’s move to RB and George Thomason’s departure to Club Brugge happened the same day (2026-08-15) — between them the club’s entire senior LB depth left in one window. Jorthy Mokio (18, LB/CDM/CM) is now the only recognised left-back on the books, and he’s a converted dual-position player rather than a specialist.',
    },
  ],
};
