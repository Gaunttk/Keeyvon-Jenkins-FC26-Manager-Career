#!/usr/bin/env node
/**
 * Player Portrait Processing Workflow
 * ------------------------------------
 * Turns raw FC26 screenshots dropped in docs/assets/inbox/ into NEW,
 * generated portrait files in docs/assets/photos/ — never the raw
 * screenshot itself. The screenshot is only ever used as an identity
 * reference; it must never end up in docs/assets/photos/.
 *
 * This script does NOT call a vision or image-generation API itself
 * (this repo has no such credentials configured). Two things happen
 * outside the script, by hand:
 *
 *   1. Identification: a Claude Code session looks at each pending
 *      screenshot with the Read tool and fills in the manifest.
 *   2. Portrait generation: a photorealistic portrait is generated
 *      (using the screenshot as identity reference) by whatever
 *      image-generation tool is available that session, and the
 *      result is dropped in docs/assets/inbox/generated/{slug}.png.
 *
 * The script only handles the mechanical, verifiable parts: tracking
 * what's new, and — critically — refusing to accept a "generated"
 * portrait that turns out to just be the original screenshot again.
 *
 * Usage:
 *   node scripts/process-player-portraits.js scan       # find new inbox images, add manifest entries
 *   node scripts/process-player-portraits.js finalize    # pull staged generated portraits into docs/assets/photos/
 *   node scripts/process-player-portraits.js status      # print a summary of the manifest
 *
 * Manifest status lifecycle:
 *   pending_identification -> identified -> generated -> verified
 *   (or skipped_exists / rejected_identical_to_source on problems)
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const INBOX_DIR = path.join(ROOT, 'docs', 'assets', 'inbox');
const STAGING_DIR = path.join(ROOT, 'docs', 'assets', 'inbox', 'generated');
const PHOTOS_DIR = path.join(ROOT, 'docs', 'assets', 'photos');
const MANIFEST_PATH = path.join(ROOT, 'docs', 'assets', 'manifests', 'player_portraits.json');

const IMAGE_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.webp', '.heic', '.heif']);

function loadManifest() {
  if (!fs.existsSync(MANIFEST_PATH)) return [];
  const raw = fs.readFileSync(MANIFEST_PATH, 'utf-8').trim();
  if (!raw) return [];
  return JSON.parse(raw);
}

function saveManifest(entries) {
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(entries, null, 2) + '\n', 'utf-8');
}

function listInboxImages() {
  if (!fs.existsSync(INBOX_DIR)) return [];
  return fs
    .readdirSync(INBOX_DIR)
    .filter((name) => IMAGE_EXTENSIONS.has(path.extname(name).toLowerCase()))
    .filter((name) => !name.startsWith('.'))
    .sort();
}

function slugify(name) {
  return name
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '') // strip accents
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

function fileHash(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

// Does a photo for this slug already exist, regardless of extension?
function existingPhotoFor(slug) {
  if (!fs.existsSync(PHOTOS_DIR)) return null;
  const match = fs
    .readdirSync(PHOTOS_DIR)
    .find((name) => path.basename(name, path.extname(name)).toLowerCase() === slug.toLowerCase());
  return match || null;
}

function cmdScan() {
  const manifest = loadManifest();
  const knownSources = new Set(manifest.map((e) => e.source));
  const images = listInboxImages();

  let added = 0;
  for (const source of images) {
    if (knownSources.has(source)) continue;
    manifest.push({
      source,
      player: null,
      slug: null,
      shirt_number: null,
      position: null,
      club: null,
      identifying_notes: null,
      status: 'pending_identification',
      output: null,
      generated_at: null,
      verified_at: null,
    });
    added += 1;
  }

  saveManifest(manifest);

  console.log(`Scanned ${images.length} image(s) in docs/assets/inbox/.`);
  console.log(`Added ${added} new manifest entr${added === 1 ? 'y' : 'ies'} needing identification.`);

  const pending = manifest.filter((e) => e.status === 'pending_identification');
  if (pending.length) {
    console.log('\nPending identification:');
    for (const e of pending) console.log(`  - ${e.source}`);
    console.log(
      '\nNext: identify these players (Claude, use the Read tool on each file in docs/assets/inbox/),\n' +
        'then fill in player/slug/shirt_number/position/club and set status to "identified" in\n' +
        'docs/assets/manifests/player_portraits.json.\n\n' +
        'Then generate a photorealistic portrait for each (using the screenshot as identity\n' +
        'reference only — never copy the screenshot itself) and save it to\n' +
        'docs/assets/inbox/generated/{slug}.png. Run this script with "finalize" afterward.'
    );
  }
}

function cmdFinalize() {
  const manifest = loadManifest();
  if (!fs.existsSync(PHOTOS_DIR)) fs.mkdirSync(PHOTOS_DIR, { recursive: true });

  let verified = 0;
  let skippedExists = 0;
  let rejectedIdentical = 0;
  let awaitingPortrait = 0;

  for (const entry of manifest) {
    if (entry.status !== 'identified') continue;

    if (!entry.slug) {
      if (entry.player) entry.slug = slugify(entry.player);
      else continue;
    }

    const existing = existingPhotoFor(entry.slug);
    if (existing) {
      entry.status = 'skipped_exists';
      entry.output = `docs/assets/photos/${existing}`;
      skippedExists += 1;
      continue;
    }

    const stagedPath = path.join(STAGING_DIR, `${entry.slug}.png`);
    if (!fs.existsSync(stagedPath)) {
      awaitingPortrait += 1;
      console.log(`  ! Awaiting generated portrait for ${entry.player} at docs/assets/inbox/generated/${entry.slug}.png`);
      continue;
    }

    const sourcePath = path.join(INBOX_DIR, entry.source);
    if (fs.existsSync(sourcePath) && fileHash(stagedPath) === fileHash(sourcePath)) {
      entry.status = 'rejected_identical_to_source';
      rejectedIdentical += 1;
      console.log(
        `  ! REJECTED ${entry.player}: docs/assets/inbox/generated/${entry.slug}.png is byte-identical to the ` +
          `original screenshot (${entry.source}). That is not a generated portrait — refusing to place it in photos/.`
      );
      continue;
    }

    const destPath = path.join(PHOTOS_DIR, `${entry.slug}.png`);
    fs.copyFileSync(stagedPath, destPath);
    entry.status = 'generated';
    entry.output = `docs/assets/photos/${entry.slug}.png`;
    entry.generated_at = new Date().toISOString();

    // Verification: the output must exist and differ from the original screenshot.
    const outputExists = fs.existsSync(destPath);
    const differsFromSource = !fs.existsSync(sourcePath) || fileHash(destPath) !== fileHash(sourcePath);
    if (outputExists && differsFromSource) {
      entry.status = 'verified';
      entry.verified_at = new Date().toISOString();
      verified += 1;
    } else {
      console.log(`  ! ${entry.player} generated but failed verification (output missing or identical to source).`);
    }
  }

  saveManifest(manifest);

  console.log(`Verified ${verified} portrait(s).`);
  if (skippedExists) console.log(`Skipped ${skippedExists} (portrait already exists in docs/assets/photos/).`);
  if (rejectedIdentical) console.log(`Rejected ${rejectedIdentical} (staged file was identical to the source screenshot).`);
  if (awaitingPortrait) console.log(`Still awaiting ${awaitingPortrait} generated portrait(s) in docs/assets/inbox/generated/.`);
}

function cmdStatus() {
  const manifest = loadManifest();
  if (!manifest.length) {
    console.log('Manifest is empty. Run "scan" first.');
    return;
  }

  const counts = {};
  for (const e of manifest) counts[e.status] = (counts[e.status] || 0) + 1;

  console.log(`${manifest.length} manifest entr${manifest.length === 1 ? 'y' : 'ies'}:`);
  for (const [status, count] of Object.entries(counts)) {
    console.log(`  ${status}: ${count}`);
  }

  console.log('\nDetail:');
  for (const e of manifest) {
    const player = e.player || '(unidentified)';
    console.log(`  [${e.status}] ${e.source} -> ${player}${e.output ? ' -> ' + e.output : ''}`);
  }
}

function main() {
  const cmd = process.argv[2];
  switch (cmd) {
    case 'scan':
      cmdScan();
      break;
    case 'finalize':
      cmdFinalize();
      break;
    case 'status':
      cmdStatus();
      break;
    default:
      console.log('Usage: node scripts/process-player-portraits.js <scan|finalize|status>');
      process.exit(cmd ? 1 : 0);
  }
}

main();
