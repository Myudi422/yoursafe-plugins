# YourSafe site plugins

Private repository for YourSafe's downloadable, data-only scraper plugins. Requires YourSafe 3.9.0 or later.

## Install on Android

Open the browser's **Plugins > Site plugins > Install / update site plugins**.
Use `Myudi422/yoursafe-plugins`, branch `main`. For private access, create a fine-grained GitHub token with access to this repository only and **Contents: Read-only**. Enter it on the phone, then **Check updates > Install / Update**. The token is encrypted with Android Keystore, is never included in the APK or this repository, and can be removed with **Forget token**.

IDLIX and MovieBox version 1 are bundled for offline first use. Installed updates override the bundled rules and survive app restarts. Removing a plugin disables its special rules; general video detection remains available. Restore bundled plugins is available without GitHub access. Reload websites after changing plugins.

## Repository layout

```
index.json
plugins/idlix/plugin.json
plugins/moviebox/plugin.json
tools/build_index.py
```

## Scraper API 1

Each plugin is a JSON object with `apiVersion: 1`, unique lowercase `id`, `name`, positive integer `version`, `description`, and a `domains` array. Domains match exactly or as subdomains, never arbitrary URL substrings.

`mediaSelectors` contains CSS selectors for elements exposing `currentSrc`, `src`, or `data-src`. Existing DOM video, network HLS/DASH/MP4, response MIME, and playback JSON discovery stay available in the app.

`subtitles` maps provider JSON to subtitle tracks. `urlKeys`, `languageKeys`, and `labelKeys` are ordered field-name lists. `containers` identifies collections containing subtitle objects, including URLs without a subtitle extension. The app retains signed URLs and normalizes language codes, including Indonesian `in_id`.

`playback` configures scoped HLS query propagation. `hosts` lists exact HTTPS hosts, `pathPrefix` selects the video namespace, `scopeSegments` binds requests to the same video path, `tokenParameter` identifies the session query parameter, and `query` contains fixed query values. `playlistPrefix` and `variantPrefix` identify disguised JSON playlists. The engine refuses HTTP, alternate ports, URL credentials, unknown hosts, and paths belonging to another video. No credentials are stored in plugin manifests.

Plugins cannot execute JavaScript, load DEX/native libraries, read the filesystem, or access the GitHub credential. Their supported operations are declarative extraction and scoped media-request rewriting. Websites requiring a different capability may require a future app API; DRM is not bypassed.

## Publish changes

Edit a manifest and increment its `version`. Run:

```
python tools/build_index.py
git add plugins index.json
git commit -m "Update site plugin"
git push
```

`build_index.py` regenerates the catalog and SHA-256 values from the exact manifest bytes. YourSafe checks the checksum and ID/version before atomically replacing a plugin, rejects downgrades, and keeps the previous installed version if validation fails. Repository access is the trust boundary: restrict write access and review plugin changes.

Do not commit API tokens, cookies, session URLs, or personal browsing captures.
