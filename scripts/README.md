# Scripts

Utility scripts for keeping generated/derived files in sync with their
sources. Most of these are Python (see each file's docstring); this file
also covers the one Node script, `process-player-portraits.js`.

Portrait generation is **manual** (via ChatGPT's web UI, not an API
script) — an earlier `generate-player-portrait.js` script that called the
OpenAI API directly was tried and dropped: cost added up ($ per image)
without consistently good results across players. Generating by hand in
ChatGPT's UI, then dropping the result into the staging folder below, has
worked better.

## process-player-portraits.js

Turns raw FC26 screenshots into **newly generated**, photorealistic
portrait files — never the raw screenshot itself. The screenshot is only
ever used as an identity reference (face, ethnicity, hairstyle, build,
shirt number, boots); the FC26 UI, ratings, and overlays must not appear
in the final portrait.

**Pipeline:**

```
docs/assets/inbox/*.jpeg                    (raw screenshots you drop in)
        |
        v  scan
docs/assets/manifests/player_portraits.json (tracks source -> player -> output)
        |
        v  identify (Claude reads each image, fills in the manifest)
        |
        v  generate (a photorealistic portrait, using the screenshot only
        |            as identity reference, dropped in the staging folder)
docs/assets/inbox/generated/{slug}.png
        |
        v  finalize (copies + hash-verifies against the source screenshot)
docs/assets/photos/{slug}.png               (final portrait, ready for HTML)
```

Nothing in this script calls a vision or image-generation API — this repo
has no such credentials configured. Two things happen by hand, in a Claude
Code session:

1. **Identification** — Claude looks at each pending screenshot with the
   Read tool (same as it already does for squad screenshots) and fills in
   the manifest.
2. **Portrait generation** — a photorealistic portrait is generated using
   the screenshot as an identity reference only, and saved to the staging
   folder. The script has no opinion on *how* this happens (it depends on
   whatever image-generation tool is available that session) — it only
   picks up the result afterward.

The script's own job is the mechanical, verifiable part: tracking what's
new, and — critically — **refusing to accept a "generated" portrait that
turns out to just be the original screenshot again** (checked by SHA-256
hash comparison, not by trusting the filename).

### Workflow

1. **Drop screenshots** into `docs/assets/inbox/` (from git, phone push,
   wherever).

2. **Scan** for new images and register them in the manifest:

   ```bash
   node scripts/process-player-portraits.js scan
   ```

   Adds one entry per new file to
   `docs/assets/manifests/player_portraits.json` with
   `"status": "pending_identification"`. Existing manifest entries are
   left untouched, so re-running `scan` is always safe.

3. **Identify the players** (done by Claude, not the script). For each
   entry with `status: "pending_identification"`, Claude reads the
   corresponding file in `docs/assets/inbox/` and edits the manifest entry
   directly:

   ```json
   {
     "source": "IMG_2262.jpeg",
     "player": "Brian Gutierrez",
     "slug": "brian_gutierrez",
     "shirt_number": "8",
     "position": "CM",
     "club": "Wrexham AFC",
     "identifying_notes": "Reference for generated portrait: light-medium skin tone, short dark brown hair, clean-shaven, slim build; red Wrexham home kit, number 8, brown boots.",
     "status": "identified",
     "output": null,
     "generated_at": null,
     "verified_at": null
   }
   ```

   Only fill in what's actually visible/confirmable in the screenshot —
   same rule as everywhere else in this project: never guess or infer.
   `identifying_notes` should capture the physical details the portrait
   generation step needs to preserve (skin tone, hair, build, kit/number,
   boots), since that step won't re-look at the raw screenshot's FC26 UI.

   `slug` should be the lowercase, underscore-separated form of the
   player's name (e.g. `"Brian Gutierrez"` -> `"brian_gutierrez"`); if you
   leave `slug` blank but set `player`, `finalize` will derive it the same
   way.

4. **Generate the portrait** for each `identified` entry, by hand, in
   ChatGPT's web UI (upload the screenshot from `docs/assets/inbox/`, and
   optionally a kit reference photo from `docs/assets/kit-references/`
   for outfield players) — a new, photorealistic image using the
   screenshot purely as an identity reference, with:
   - the player's face, ethnicity, hairstyle, build, shirt number, and
     boots preserved from the screenshot
   - all FC26 UI, HUD, ratings, and overlay elements removed
   - a realistic football match or media-day look, Wrexham kit, blurred
     stadium crowd background, no text/overlays

   Save the result to `docs/assets/inbox/generated/{slug}.png` — e.g.
   `docs/assets/inbox/generated/brian_gutierrez.png`.

5. **Finalize** — pull staged portraits into `docs/assets/photos/`:

   ```bash
   node scripts/process-player-portraits.js finalize
   ```

   For every entry with `status: "identified"`:
   - If a photo for that slug already exists in `docs/assets/photos/`
     (any extension), the entry is marked `"skipped_exists"` and nothing
     is overwritten.
   - If no file exists yet at `docs/assets/inbox/generated/{slug}.png`,
     the entry is left as `"identified"` and reported as awaiting a
     portrait.
   - If a staged file exists, its SHA-256 hash is compared against the
     original screenshot's hash. **If they match, the file is rejected**
     (status `"rejected_identical_to_source"`) and never placed in
     `docs/assets/photos/` — this is the guard against accidentally
     copying the raw screenshot forward.
   - Otherwise the staged file is copied to
     `docs/assets/photos/{slug}.png`, the entry moves to `"generated"`
     with an `output` path and `generated_at` timestamp, and it's
     immediately re-checked (output file exists, hash differs from the
     source screenshot) — passing that check moves it to `"verified"`
     with a `verified_at` timestamp.

6. **Check status anytime:**

   ```bash
   node scripts/process-player-portraits.js status
   ```

   Prints a count by status plus a one-line summary per manifest entry.

### Manifest status lifecycle

```
pending_identification -> identified -> generated -> verified
                                      \-> skipped_exists
                                      \-> rejected_identical_to_source
```

### Notes

- The manifest is the permanent record linking
  `source screenshot -> identified player -> final portrait filename`.
  Don't hand-edit `output`/`status`/`generated_at`/`verified_at` after the
  fact — those are written by `finalize`.
- The script never deletes anything from `docs/assets/inbox/`. Once a
  screenshot's portrait has been generated, verified, and committed, clear
  the screenshot out of the inbox with `git rm` in the same commit, per
  this project's usual screenshot-cleanup rule (see the root `CLAUDE.md`).
  Staged files in `docs/assets/inbox/generated/` should be cleared out the
  same way once their entry reaches `"verified"`.
- Re-running `scan` / `finalize` is idempotent — already-known sources are
  skipped on `scan`, and already-verified/already-existing portraits are
  skipped on `finalize`.
