# Scripts

Utility scripts for keeping generated/derived files in sync with their
sources. Most of these are Python (see each file's docstring); this file
also covers the one Node script, `process-player-portraits.js`.

## process-player-portraits.js

Turns raw player screenshots into named portrait files, without ever
requiring manual renaming.

**Pipeline:**

```
docs/assets/inbox/*.jpeg           (raw screenshots you drop in)
        |
        v  scan
docs/assets/manifests/player_portraits.json   (tracks source -> player -> output)
        |
        v  identify (Claude reads each image, fills in the manifest)
        |
        v  apply
docs/assets/photos/{slug}.{ext}    (final portrait, ready for use in HTML)
```

The script does **not** call a vision API itself — this repo has no vision
API credentials configured. Identification happens in a Claude Code
session, where Claude looks at each pending image with the Read tool
(same as it already does for squad screenshots) and fills in the
manifest. The script only handles the mechanical parts: tracking what's
new, and copying/renaming into `docs/assets/photos/` once a player is
identified.

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

3. **Identify the players** (this step is done by Claude, not the
   script). For each entry with `status: "pending_identification"`,
   Claude reads the corresponding file in `docs/assets/inbox/` and edits
   the manifest entry directly:

   ```json
   {
     "source": "IMG_2262.jpeg",
     "player": "Brian Gutierrez",
     "slug": "brian_gutierrez",
     "shirt_number": "8",
     "position": "CM",
     "club": "Wrexham AFC",
     "identifying_notes": "Confirmed by shirt name + squad photo background",
     "status": "identified",
     "output": null,
     "processed_at": null
   }
   ```

   Only fill in what's actually visible/confirmable in the screenshot —
   same rule as everywhere else in this project: never guess or infer.
   If a player can't be identified, leave `status` as
   `"pending_identification"` (or set it to `"unidentified"` with a note
   in `identifying_notes`) rather than making something up.

   `slug` should be the lowercase, underscore-separated form of the
   player's name (e.g. `"Brian Gutierrez"` -> `"brian_gutierrez"`); if
   you leave `slug` blank but set `player`, `apply` will derive it for
   you the same way.

4. **Apply** the manifest to generate portraits:

   ```bash
   node scripts/process-player-portraits.js apply
   ```

   For every entry with `status: "identified"`:
   - If a photo for that slug already exists in `docs/assets/photos/`
     (any extension), the entry is marked `"skipped_exists"` and nothing
     is overwritten.
   - Otherwise, the source image is copied from `docs/assets/inbox/` to
     `docs/assets/photos/{slug}{ext}` (same extension as the source —
     screenshots are usually `.jpeg`/`.png`/`.webp`, and renaming the
     bytes to `.png` without actually converting them would produce a
     broken image). The entry is updated to `"generated"` with its
     `output` path and a `processed_at` timestamp.

5. **Check status anytime:**

   ```bash
   node scripts/process-player-portraits.js status
   ```

   Prints a count by status plus a one-line summary per manifest entry.

### Notes

- The manifest is the permanent record linking
  `source screenshot -> identified player -> final portrait filename`.
  Don't hand-edit `output`/`status`/`processed_at` after the fact — those
  are written by `apply`.
- The script never deletes anything from `docs/assets/inbox/`. Once a
  screenshot's portrait has been generated (and committed), clear it out
  of the inbox with `git rm` in the same commit, per this project's
  usual screenshot-cleanup rule (see the root `CLAUDE.md`).
- Re-running `scan` / `apply` is idempotent — already-known sources are
  skipped on `scan`, and already-generated/already-existing portraits are
  skipped on `apply`.
