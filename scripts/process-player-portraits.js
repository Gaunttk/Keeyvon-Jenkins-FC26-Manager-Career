#!/usr/bin/env node
/**
 * Player Portrait Processing Workflow
 * ------------------------------------
 * Turns raw screenshots dropped in docs/assets/inbox/ into named portrait
 * files in docs/assets/photos/, tracked through a manifest so the link
 * between "source screenshot" -> "identified player" -> "final portrait
 * filename" is never lost.
 *
 * This script does NOT call a vision API itself (this repo has no API
 * credentials configured for that). Identification is done by a Claude
 * Code session actually looking at the images with the Read tool, then
 * filling in the manifest. See scripts/README.md for the full workflow.
 *
 * Usage:
 *   node scripts/process-player-portraits.js scan     # find new inbox images, add manifest entries
 *   node scripts/process-player-portraits.js apply     # generate portraits from identified entries
 *   node scripts/process-player-portraits.js status    # print a summary of the manifest
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const INBOX_DIR = path.join(ROOT, 'docs', 'assets', 'inbox');
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
      processed_at: null,
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
        'docs/assets/manifests/player_portraits.json. Run this script with "apply" afterward.'
    );
  }
}

function cmdApply() {
  const manifest = loadManifest();
  if (!fs.existsSync(PHOTOS_DIR)) fs.mkdirSync(PHOTOS_DIR, { recursive: true });

  let generated = 0;
  let skippedExists = 0;
  let skippedMissingSlug = 0;
  let skippedMissingSource = 0;

  for (const entry of manifest) {
    if (entry.status !== 'identified') continue;

    if (!entry.slug) {
      if (entry.player) entry.slug = slugify(entry.player);
      else {
        skippedMissingSlug += 1;
        continue;
      }
    }

    const existing = existingPhotoFor(entry.slug);
    if (existing) {
      entry.status = 'skipped_exists';
      entry.output = `docs/assets/photos/${existing}`;
      skippedExists += 1;
      continue;
    }

    const sourcePath = path.join(INBOX_DIR, entry.source);
    if (!fs.existsSync(sourcePath)) {
      skippedMissingSource += 1;
      console.log(`  ! Missing source file for ${entry.source} (${entry.player || 'unknown player'})`);
      continue;
    }

    const ext = path.extname(entry.source).toLowerCase();
    const outName = `${entry.slug}${ext}`;
    const outPath = path.join(PHOTOS_DIR, outName);

    fs.copyFileSync(sourcePath, outPath);

    entry.status = 'generated';
    entry.output = `docs/assets/photos/${outName}`;
    entry.processed_at = new Date().toISOString();
    generated += 1;
  }

  saveManifest(manifest);

  console.log(`Generated ${generated} portrait(s).`);
  if (skippedExists) console.log(`Skipped ${skippedExists} (portrait already exists in docs/assets/photos/).`);
  if (skippedMissingSlug) console.log(`Skipped ${skippedMissingSlug} (identified but missing a player/slug).`);
  if (skippedMissingSource) console.log(`Skipped ${skippedMissingSource} (source file no longer in inbox).`);
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
    case 'apply':
      cmdApply();
      break;
    case 'status':
      cmdStatus();
      break;
    default:
      console.log('Usage: node scripts/process-player-portraits.js <scan|apply|status>');
      process.exit(cmd ? 1 : 0);
  }
}

main();
