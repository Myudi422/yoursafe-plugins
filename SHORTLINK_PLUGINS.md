# Shortlink API 2 — YourSafe 4.0.0

Plugin shortlink dipisahkan dari **video scraper API 1**. Kedua jenis memakai katalog, versi otomatis, checksum dan auto install/update yang sama. Aplikasi menampilkan kategori Video scrapers dan Shortlinks. APK sebelum 4.0.0 tidak memiliki runtime shortlink ini; penolakan API yang belum didukung tidak mengubah scraper video yang sudah terpasang.

## Kemampuan yang tersedia

Script JavaScript sinkron menerima snapshot terbatas halaman dan mengembalikan URL tujuan. Script berjalan dengan Rhino 1.8.1 pada **service Android ber-UID terisolasi**, bukan di JavaScript halaman browser. Proses worker tidak menginisialisasi VPN, downloader atau penyimpanan aplikasi.

Runtime ini **bukan emulator Tampermonkey**: tidak ada `GM_*`, `unsafeWindow`, DOM langsung, `fetch`, XHR, cookie, clipboard, file, kelas Java, popup, timer halaman, submit form atau akses API native. Tidak ada resolver pihak ketiga. JavaScript dapat melakukan perhitungan/JSON/string dan memakai helper `atob`; ia hanya mendapat data yang dijelaskan di bawah.

Contoh bentuk manifest (domain dummy hanya untuk dokumentasi):

```json
{
  "apiVersion": 2,
  "type": "shortlink",
  "id": "shortlink-example",
  "name": "Example",
  "description": "Membuka link tujuan yang tersedia di halaman.",
  "domains": ["short.example"],
  "selectors": ["a#destination"],
  "permissions": ["page.links", "navigation.resolve"],
  "script": "function resolve(input) { return input.links.length ? {url: input.links[0].href} : null; }"
}
```

`version` dikelola bot. Script di-embed dalam manifest agar kode, versi, dan checksum diterbitkan bersama. Mengubah `script` menaikkan versi otomatis. Nama/deskripsi untuk pengguna tetap netral, tanpa nama layanan hosting repo.

## Input dan output

`resolve(input)` menerima objek JSON:

```json
{
  "url": "https://short.example/page?r=example",
  "host": "short.example",
  "path": "/page",
  "query": {"r": "example"},
  "links": [{"selector": "a#destination", "href": "https://destination.example/file"}]
}
```

- Host dokumen harus cocok dengan `domains`; domain mirip tidak diterima. Sumber harus HTTPS port 443 tanpa kredensial URL.
- Input berasal dari URL tab dan collector DOM bawaan, bukan menjalankan script plugin dalam WebView.
- Maksimal 8 selector CSS (masing-masing 200 karakter), 32 link dan 32 nama parameter query. Collector hanya membaca atribut `href`, bukan HTML, nilai input, cookie atau storage halaman.
- Script dan input masing-masing maksimal 64 KiB; hasil maksimal 16 KiB.
- Kembalikan `null` jika belum ada tujuan, atau objek `{ "url": "https://..." }`. URL relatif diselesaikan terhadap halaman sumber oleh aplikasi.
- Tujuan dibatasi HTTPS port 443, tanpa userinfo, dengan hostname DNS yang lolos kebijakan. Skema `javascript:`, `file:`, `intent:`, HTTP, alamat IP literal, `.local`, `.localhost`, `.internal` dan `.home.arpa` ditolak. Ini bukan klaim bahwa setiap domain publik pasti bebas phishing atau DNS rebinding; browser tetap memuat situs tujuan sebagai konten web biasa.
- Mengembalikan objek lain, Promise, markup atau perintah native tidak menambah kemampuan.

## Batas eksekusi dan navigasi

- Interpreter membatasi sekitar 100.000 instruksi, deadline pemeriksaan 250 ms dan kedalaman stack 128. Hitungan instruksi/deadline tidak menjamin batas memori untuk semua operasi native JavaScript.
- Watchdog service mengakhiri proses worker jika eksekusi tidak selesai dalam 1,2 detik, termasuk operasi yang tidak melewati observer instruksi. Client juga memiliki timeout dan menangani worker yang mati. Saat unbind/destroy, worker terisolasi dihentikan.
- Browser melakukan paling banyak 20 pemeriksaan link dengan jeda 500 ms untuk halaman yang sedang aktif/terlihat; waktu snapshot dan IPC dapat menambah durasi. Snapshot yang sama tidak dieksekusi terus-menerus.
- Navigasi dibatalkan bila pengguna pindah halaman/tab, plugin berubah/dihapus, atau browser tidak aktif. Satu rantai dibatasi lima hop dan loop ditolak. Riwayat rantai direset setelah jeda lebih dari 30 detik atau ketika pengguna memasuki sumber baru yang tidak termasuk rantai tersebut.
- Navigasi plugin yang sudah tervalidasi memakai izin satu kali untuk URL persis tersebut, bukan mematikan Anti-Redirect secara global.
- Tidak menyelesaikan CAPTCHA, memalsukan pesan verifikasi, melewati login/DRM atau mengirim URL ke layanan bypass eksternal.


## Sebelum halaman dimuat — YourSafe 4.0.1

Plugin dengan `selectors: []` diperlakukan sebagai resolver yang hanya membutuhkan URL. Pada YourSafe 4.0.1, klik navigasi utama GET dengan gesture pengguna, input alamat, dan pembukaan tab baru melalui aplikasi diproses sebelum `loadUrl` untuk shortlink. Script tetap berjalan di worker terisolasi, memakai input `links: []`.

Untuk pola CLK `/full?url=Base64` yang valid, permintaan navigasi awal dibatalkan secara sinkron, lalu hanya URL HTTPS hasil resolusi yang dimuat. Halaman asal seperti OvaGames tidak diubah: link unduhannya menuju tujuan asli saat ditekan. Ini tidak menghapus iklan pada halaman asal atau melewati verifikasi di situs tujuan.

Decoder CLK versi awal disertakan di APK agar langsung tersedia tanpa menunggu koneksi atau auto install pertama. Pembaruan repo tetap menggantikannya seperti biasa. Penghapusan plugin secara eksplisit tetap dihormati. APK lama masih memakai jalur setelah halaman dimuat.

Skrip yang mengembalikan `null` menandakan format URL tersebut tidak ditangani dan navigasi normal dapat dilanjutkan. Jika worker gagal saat pre-navigation, aplikasi mempertahankan halaman asal dan memberi pesan untuk mencoba lagi; tidak diam-diam memuat halaman iklan sebagai fallback. Navigasi baru, perpindahan tab atau perubahan halaman membatalkan hasil lama. Redirect sintetis tanpa gesture dari halaman biasa tetap melewati perlindungan Anti-Redirect normal.

## Penggantian href OvaGames — YourSafe 4.0.2

Pada halaman HTTPS `ovagames.com` beserta subdomainnya, collector bawaan membaca anchor CLK `/full?url=Base64` dan meminta plugin `shortlink-clk-sh` yang terpasang untuk mendekodenya di worker terisolasi. Setelah tujuan tervalidasi, aplikasi mengganti atribut `href` anchor yang masih cocok dengan sumber persisnya. Teks link dan atribut `target` tetap dipertahankan, sehingga copy link dan buka tab baru memakai tujuan aslinya setelah penggantian selesai. MutationObserver menangani link yang ditambahkan belakangan.

Bridge dibatasi ke origin OvaGames dan pesan dari frame utama, memerlukan dukungan WebView `WEB_MESSAGE_LISTENER`. Collector memeriksa maksimal 1.000 anchor dan 16 sumber unik per batch; antrean dan cache dibatasi masing-masing 128 entri. Hasil halaman lama, plugin yang berubah/dihapus, dan tujuan yang tidak lolos validasi diabaikan. Link yang belum berhasil didekode tetap memakai href awal, dengan resolver sebelum navigasi sebagai cadangan. Perubahan hanya berlaku pada DOM lokal halaman tersebut, tidak mengubah server OvaGames atau menghapus iklan/verifikasi situs tujuan. Muat ulang tab setelah memperbarui APK. Penghapusan plugin menghentikan penggantian selanjutnya; muat ulang untuk mendapatkan kembali href asli dari server.

Ini kemampuan collector khusus yang diimplementasikan pada APK 4.0.2, bukan permission baru untuk script mengubah DOM secara bebas. Pengujian mencakup simulasi DOM (copy/tab baru, link dinamis, hasil kedaluwarsa) dan integrasi JVM dengan decoder sandbox; keduanya bukan pengujian situs live di perangkat.

## Penggantian href umum — YourSafe 4.0.3

Mekanisme 4.0.3 menggantikan pembatasan khusus OvaGames/CLK di atas. Pada halaman HTTPS port 443 tanpa kredensial URL, aplikasi membaca anchor yang domain tujuannya cocok dengan plugin shortlink terpasang **dan `selectors: []`**. Plugin menerima URL anchor tersebut dengan `links: []`, bukan DOM halaman asal. Tidak ada daftar domain sumber atau ID plugin khusus di mesin penggantian href. Plugin baru maupun perubahan domain otomatis ikut setelah auto install/update; tidak membutuhkan APK baru selama kontrak API 2 saat ini cukup.

Gunakan plugin URL-only untuk decoder parameter, perhitungan lokal, atau pemetaan URL yang benar-benar diketahui. Script mengembalikan `null` untuk pola yang tidak ditangani. Plugin yang perlu membaca DOM halaman shortlink (`selectors` tidak kosong), akses jaringan, CAPTCHA atau interaksi tombol tidak dapat diselesaikan dari anchor di halaman asal. Alur setelah navigasi tetap tersedia untuk plugin berbasis DOM. Menambah manifest tidak memberikan permission tambahan.

Collector bawaan tetap satu-satunya kode yang membaca/mengganti DOM; script plugin tetap di worker terisolasi. Bridge menerima pesan hanya dari frame utama HTTPS dengan origin yang cocok dengan WebView saat ini. Tidak ada akses cookie, HTML, storage atau API native melalui bridge. Validasi sumber/tujuan, perubahan halaman, plugin dihapus/diubah, dan tab tidak aktif diperiksa kembali di aplikasi.

Tautan dinamis ikut diproses. Collector memindai maksimal 1.000 anchor per giliran, melanjutkan ke anchor berikutnya, mengirim maksimal 16 sumber unik per batch, lalu menunggu batch selesai. Maksimal 2.048 sumber dicoba per konfigurasi halaman; cache native 128 entri dan antrean 128. Link tidak didukung tidak menghalangi batch selanjutnya. Penggantian berlangsung asinkron; sebelum selesai, href asli masih tersedia dan resolver sebelum navigasi tetap menjadi cadangan. Teks/target link dipertahankan. Hanya anchor DOM dokumen utama yang diproses, bukan URL dalam teks biasa, handler JavaScript, shadow DOM atau iframe.

Rantai resolver dibatasi lima hop; loop membatalkan penggantian. Semua hop tetap divalidasi dan perubahan konfigurasi membatalkan hasil lama. Link yang sudah diganti tetap memakai tujuan terakhir sampai halaman dimuat ulang. Muat ulang juga untuk mencoba ulang sumber yang sebelumnya gagal tanpa perubahan konfigurasi. WebView harus mendukung `WEB_MESSAGE_LISTENER`; provider lama tetap memakai resolver navigasi.

Pengujian mencakup domain plugin baru pada halaman lain, rantai lintas plugin, loop, tujuan tidak aman, penghapusan plugin saat resolusi, link dinamis, batch di atas 1.000 anchor, serta copy/tab baru melalui href yang diganti. Tes JVM/DOM tidak membuktikan keberhasilan situs live di perangkat.

## Source-page link helpers — API 3 / YourSafe 4.0.4

API 3 adds one explicitly scoped capability to the existing isolated shortlink runtime. A source-page helper matches the **current page** against `domains`, then resolves outbound HTTPS anchors matching its path and query rules regardless of their destination domain. API 1 video scrapers and API 2 shortlink helpers remain supported. Older APKs reject API 3 instead of treating source-page domains as ordinary shortlink hosts.

```json
{
  "apiVersion": 3,
  "type": "shortlink",
  "id": "ovagames-links",
  "name": "OvaGames",
  "description": "Replaces encoded full links with their original HTTPS destinations on OvaGames, regardless of the shortlink domain.",
  "domains": ["ovagames.com"],
  "scope": "source-page",
  "outbound": {"paths": ["/full", "/full/"], "queryParameter": "url"},
  "selectors": [],
  "permissions": ["page.links", "navigation.resolve"],
  "script": "function resolve(input) { /* Decode input.query.url, or return null. */ return null; }"
}
```

The example script illustrates the contract; the published OvaGames manifest contains the actual local Base64 decoder. Versions remain bot-managed. New API 3 plugins must have `scope: "source-page"`, empty selectors, one to eight exact paths (maximum 200 characters, letters/digits/slashes/underscores/hyphens), and a query parameter name of one to 40 letters/digits/underscores/hyphens. Wildcard paths and new permissions are not supported. API 1/2 manifests must not declare this scope or outbound rules.

Both the collector and native runtime check the source-page scope; lookalike domains and non-HTTPS pages do not qualify. Outbound URLs and resolved destinations still require HTTPS port 443 without credentials. Only the URL is sent to the sandbox with `links: []`; the helper gains no DOM, network, cookie, storage, or native access. `api` parameters are not used by the decoder, and no user's API values are included in the manifests. Invalid Base64, unsupported paths, empty query values, unsafe destinations, and loops leave links unchanged. These rules do not decode opaque short codes or bypass verification at the destination.

Source-page helpers run before domain resolvers for qualifying anchors; returning null allows an existing domain resolver to try. All existing dynamic-link, batching, cancellation, generation, destination-validation, and five-hop limits apply. Cache entries include the source page so a result cannot be reused outside its authorized context. Gesture-driven clicks on matching links can also resolve before navigation if href rewriting has not completed; synthetic redirects retain normal protection. Standalone shortlinks outside OvaGames continue through their domain plugins. Already rewritten hrefs remain until a page reload.

OvaGames version 1 is bundled in 4.0.4 for first use and offline upgrades, then updated through the public catalog. Explicit removal remains respected. Names/descriptions in the plugin UI are English, and the helper appears as **Website link helper**. Tests cover unknown outbound domains, source-domain lookalikes, unrelated pages/cache isolation, malformed/unsafe destinations, early clicked-link resolution, schema rejection, and existing API 2 behavior. Automated tests are not a claim of live website or physical-device validation.

## Modul awal yang diadaptasi

| Plugin | Sumber pola | Cakupan aktual |
| --- | --- | --- |
| `shortlink-linkvertise` | Cabang lokal `r` pada `extra_bypasses/apis.user.js` | Decode parameter base64 `r`, lalu validasi tujuan HTTPS. Kasus yang memerlukan resolver/server eksternal tidak didukung. |
| `shortlink-acortalink` | Selector `a.button#contador` pada `extra_bypasses/acortalink.user.js` | Membuka URL pada anchor yang sudah tersedia. Tidak menyalin spoofing `postMessage`, manipulasi popup, CAPTCHA, atau algoritma verifikasi upstream. |
| `shortlink-clk-sh` | Format `/full?url=Base64` yang diamati pada link pengguna | Decode lokal parameter `url` menjadi tujuan HTTPS. Parameter `api` tidak dipakai/disimpan; tidak memanggil resolver eksternal. Link kode pendek tanpa parameter tujuan tidak termasuk cakupan ini. |
| `shortlink-shrinkearn` | Format `shrinkearn.com/full?url=Base64` yang diamati pada link pengguna | Decode lokal tujuan HTTPS; `api` tidak digunakan. Pada 4.0.3, anchor pada halaman asal ikut diganti oleh mekanisme umum setelah plugin tersinkronisasi. Link kode pendek tanpa parameter tujuan tidak termasuk cakupan ini. |

Provenance dan batas adaptasi ada di `attribution` setiap manifest serta [THIRD_PARTY.md](THIRD_PARTY.md). Ini bukan port semua domain/fitur repo upstream. Jangan menambahkan manifest domain yang belum diamati atau menjanjikan shortlink terproteksi selesai hanya karena halaman cocok.

## Pengujian dan perubahan kemampuan

Generator mendukung API 1/video dan API 2/shortlink. Untuk generator/workflow jalankan `python -m unittest discover -s tools -p 'test_*.py'`. Runtime aplikasi memiliki tes untuk akses Java yang ditolak, loop, input/output besar, scope terpisah, validasi URL, pembatasan rantai, auto install dan kedua modul contoh.

Tes JVM/simulasi tidak membuktikan binder, UID isolasi atau situs live berhasil di perangkat. Pengujian perangkat nyata harus memeriksa proses `:shortlink_sandbox`, navigasi saat tab berubah, kematian worker dan alur situs dengan sesi yang valid. Jangan menyatakan cakupan 400+ domain atau semua kasus situs berdasarkan dua modul awal ini.

Jika membutuhkan API jaringan, UI deklaratif, storage plugin, collector tambahan atau aksi submit/click, definisikan dan implementasikan kemampuan runtime baru beserta validasi dan pengujiannya terlebih dahulu. Jangan menambahkan permission/field yang belum dilayani aplikasi.
