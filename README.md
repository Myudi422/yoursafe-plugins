# YourSafe video site plugins

Public catalog of data-only video scraper plugins. **IDLIX** and **MovieBox** remain available. All shortlink/bypass plugins have been removed from this repository and application source, including their script sandbox and network broker. Existing APKs retain installed capabilities until updated; catalog deletion alone does not uninstall cached plugins on those versions.

## Install and update

Open **Plugins → Site plugins**. The public catalog needs no account or token. New video plugins and updates synchronize automatically on app foreground. Successful checks have a five-minute cooldown per process; failed checks can retry after one minute on reopening. Removed plugins stay disabled until manually reinstalled. Failed updates keep existing rules; active downloads keep their session snapshots.

IDLIX and MovieBox are bundled for offline use. Updated source preserves installed video updates and removal preferences while discarding unsupported cached formats. Restore default plugins restores only these video scrapers. Reload websites after changing extraction rules.

## Supported format

Only **API 1**, type `video` (or omitted), is supported:

- `domains`: exact domains/subdomains.
- `mediaSelectors`: recognized DOM video sources.
- `subtitles`: URL/language/label/container mapping for subtitle metadata.
- `playback`: validated, narrowly scoped HLS session/query rules.

General HLS/DASH/MP4 network and DOM discovery remain part of the app. Manifests cannot execute JavaScript, add UI, access files, or make arbitrary network requests. See [SITE_PLUGINS.md](SITE_PLUGINS.md) for schema/limits and [AGENTS.md](AGENTS.md) for AI instructions.

## Publish

Add or edit `plugins/<site-id>/plugin.json` on `main`. Do not edit versions or `index.json` manually. **Update plugin index** validates manifests, increments versions only for content changes, regenerates hashes/catalog entries, and commits them together. New plugins start at version 1. Formatting and manual version changes do not bump versions. Deleting a manifest removes it from the next catalog.

Run `python -m unittest discover -s tools -p 'test_*.py'` for generator changes. Wait for the workflow to succeed; distribution caches may delay visibility. YourSafe validates schema, ID, version, and checksum before replacement.

Keep UI names/descriptions in English. Never publish credentials, private captures, or active signed media URLs.
