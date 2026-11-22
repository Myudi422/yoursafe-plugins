# YourSafe site plugins

**YourSafe 4.0.2:** on HTTPS OvaGames pages, supported CLK full links are also rewritten in the actual anchor `href`. Copy link and open in new tab therefore use the decoded destination after replacement. Links added dynamically are observed too. The native collector invokes the installed CLK plugin in its isolated worker; plugin scripts still have no direct DOM access. This requires a WebView supporting origin-scoped web messaging. Pre-navigation resolution remains available as a fallback. Reload an existing OvaGames tab after updating the APK.

**YourSafe 4.0.1:** video scrapers (API 1) and isolated JavaScript shortlink helpers (API 2) are separate plugin types. Both support automatic installation, updates, versions and checksums. See [SHORTLINK_PLUGINS.md](SHORTLINK_PLUGINS.md) for the runtime contract, initial Linkvertise/Acortalink coverage and limits, and [THIRD_PARTY.md](THIRD_PARTY.md) for provenance. Existing video manifests remain API 1.

Public repository for YourSafe's downloadable, data-only scraper plugins. Use YourSafe 4.0.1 for both plugin types and pre-navigation resolution of URL-only shortlinks. The CLK decoder is bundled for immediate availability; a valid full link opens its destination without loading the shortlink page. Older 3.9.x builds support video rules only. No user credentials are required.

## Install on Android

Open the browser's **Plugins > Site plugins > Install / update site plugins**. The public catalog loads automatically. On YourSafe 3.9.3 and later, new website plugins are added automatically when the app opens. Manual Install remains available to re-enable a removed plugin. Starting in YourSafe 3.9.2, installed plugins check for newer versions and update automatically when the app enters the foreground. No GitHub account, token, or Workers service is needed.

YourSafe 3.9.1 fetches files directly from `raw.githubusercontent.com/Myudi422/yoursafe-plugins/main/` without authentication and removes obsolete private-repository credential settings. The refresh button checks for new catalog versions. Automatic updates run in the background without delaying startup, at most once per five minutes per app process (failed checks can retry after one minute on reopening). Starting in YourSafe 3.9.3, newly discovered website plugins are installed automatically on app foreground checks as well. Explicitly removed plugins stay disabled until manually installed again. Previously removed bundled plugins are respected during migration. Checksums and schemas are validated before replacing each plugin; failed updates keep the old version, and active downloads retain their original playback rules. Updated extraction settings are supplied to existing browser tabs without forcing a reload.
IDLIX and MovieBox version 1 are bundled for offline first use. Installed updates override the bundled rules and survive app restarts. Removing a plugin disables its special rules; general video detection remains available. Restore bundled plugins is available without GitHub access. Reload websites after changing plugins.

## Repository layout

Untuk AI dan penulis plugin: mulai dari [AGENTS.md](AGENTS.md), lalu baca [panduan kemampuan plugin situs](SITE_PLUGINS.md) untuk schema, contoh, batas runtime, dan cara pengujian.

```
index.json
plugins/idlix/plugin.json
plugins/moviebox/plugin.json
tools/build_index.py
```

## Scraper API 1

Each plugin is a JSON object with `apiVersion: 1`, unique lowercase `id`, `name`, automatically managed integer `version`, `description`, and a `domains` array. Domains match exactly or as subdomains, never arbitrary URL substrings.

`mediaSelectors` contains CSS selectors for elements exposing `currentSrc`, `src`, or `data-src`. Existing DOM video, network HLS/DASH/MP4, response MIME, and playback JSON discovery stay available in the app.

`subtitles` maps provider JSON to subtitle tracks. `urlKeys`, `languageKeys`, and `labelKeys` are ordered field-name lists. `containers` identifies collections containing subtitle objects, including URLs without a subtitle extension. The app retains signed URLs and normalizes language codes, including Indonesian `in_id`.

`playback` configures scoped HLS query propagation. `hosts` lists exact HTTPS hosts, `pathPrefix` selects the video namespace, `scopeSegments` binds requests to the same video path, `tokenParameter` identifies the session query parameter, and `query` contains fixed query values. `playlistPrefix` and `variantPrefix` identify disguised JSON playlists. The engine refuses HTTP, alternate ports, URL credentials, unknown hosts, and paths belonging to another video. No credentials are stored in plugin manifests.

Video scraper manifests (API 1) cannot execute JavaScript, load DEX/native libraries, read the filesystem, or access application credentials. API 2 shortlink scripts run only through the isolated snapshot/resolve contract described in SHORTLINK_PLUGINS.md. Their supported operations are declarative extraction and scoped media-request rewriting. Websites requiring a different capability may require a future app API; DRM is not bypassed.

## Publish changes

Add or edit `plugins/<site-id>/plugin.json` on the `main` branch, including through GitHub's web editor. You do not need to edit `version` or `index.json`. New plugins can omit `version`; the bot sets it to 1.

GitHub Actions compares plugin content against its last published snapshot, automatically increments the version of each changed plugin, regenerates `index.json`, and commits the manifests and catalog together using `github-actions[bot]`. It handles added, edited and deleted plugins and recalculates SHA-256 hashes. No local script, GitHub token in the app, or APK update is needed.

Wait for **Actions > Update plugin index** to finish successfully, then open or refresh **Site plugins** in YourSafe. GitHub's raw-file cache can take a short time to reflect a new commit. Invalid plugin JSON fails the workflow and leaves the previous generated catalog intact; check the run log, fix the manifest and commit again.

The workflow also runs when the index generator or workflow changes, and can be run manually with **Run workflow**. It commits changed plugin versions and `index.json` together, and retries if another commit arrives while it is running. Unchanged plugins keep their versions. Re-running the workflow does not bump a version again; whitespace/key-order changes and edits to the version field alone do not count as content updates. The bot manages the version field, so manual version numbers are normalized automatically.

The generator remains available for optional local previews:

```
python tools/build_index.py
```

`build_index.py` regenerates the catalog and SHA-256 values from the exact manifest bytes. YourSafe checks the checksum and ID/version before atomically replacing a plugin, rejects downgrades, and keeps the previous installed version if validation fails. Repository access is the trust boundary: restrict write access and review plugin changes.

Do not commit API tokens, cookies, session URLs, or personal browsing captures.
