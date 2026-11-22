# Kemampuan plugin situs YourSafe

Dokumen ini khusus **scraper video API 1**. YourSafe 4.0.0 juga mendukung **shortlink API 2** dengan sandbox dan kontrak terpisah; baca [SHORTLINK_PLUGINS.md](SHORTLINK_PLUGINS.md). Batas JavaScript di bawah mengacu pada manifest video API 1, bukan tipe shortlink baru.

Panduan untuk pengembang dan AI. Mengacu pada **Scraper API 1** dan aplikasi **YourSafe 3.9.3**. Jika runtime aplikasi berubah, perbarui dokumen ini berdasarkan kode yang benar-benar dipakai.

## Apa sebenarnya plugin situs?

Plugin adalah file **aturan JSON** yang dibaca mesin YourSafe. Pengguna membuka situs melalui browser YourSafe; mesin mengamati DOM video serta permintaan/respons media, lalu menggunakan aturan situs yang terpasang.

Alurnya:

```text
Halaman/player situs dibuka pengguna
    → deteksi umum YourSafe + aturan plugin situs
    → URL video, format, metadata subtitle, konteks sesi
    → player atau downloader bawaan YourSafe
    → video dan soft subtitle tersimpan untuk pemutaran offline
```

Jadi, kegunaannya lebih luas dari sekadar mengambil link download: aturan juga dapat membantu **pemutaran**, **subtitle**, dan **permintaan media yang memerlukan sesi**. Namun plugin ini bukan sistem scraping umum untuk semua jenis isi website.

## Peta kemampuan

| Kebutuhan | Dukungan saat ini | Bagian yang mengerjakan |
| --- | --- | --- |
| Menemukan video pada DOM/player situs | Ya, dengan batas pola URL/format yang dikenali mesin | Detektor umum + `mediaSelectors` |
| Menemukan HLS, DASH, MP4 dari aktivitas jaringan | Ya, untuk URL/MIME/pola yang dikenali mesin | Detektor umum aplikasi |
| Mengenali playlist JSON tersamar seperti IDLIX | Ya, melalui aturan namespace/host/prefix yang sesuai | `playback` + mesin HLS |
| Memetakan bahasa dan URL subtitle dari respons JSON | Ya | `subtitles` |
| Memakai soft subtitle saat streaming/offline | Ya, jika subtitle berhasil ditemukan dan disimpan | Player/downloader aplikasi |
| Mengunduh video beserta audio pendamping | Ya, untuk format yang didukung engine | Downloader aplikasi |
| Mempertahankan konteks sesi browser yang sudah tersedia | Ya, sesuai penanganan header/cookie engine; plugin tidak menyimpan cookie | Browser + sesi HTTP aplikasi |
| Menyalin token query ke segmen/key HLS dalam lingkup video yang sama | Ya, terbatas pada host/path yang diizinkan | `playback` |
| Ekstraksi audio musik umum atau konversi MP3 | Bukan kemampuan mandiri API plugin situs | Fitur/engine terpisah bila tersedia |
| Scraping gambar, PDF, ZIP, seluruh artikel atau semua file halaman | Belum ada API khusus dalam plugin situs | Unduhan file umum aplikasi adalah fitur terpisah |
| Katalog film, daftar episode, pencarian judul, poster dan halaman UI baru | Belum didukung manifest situs | Perlu pengembangan mesin/UI aplikasi |
| Menjalankan `scraper.js`, Python, DEX, library native atau perintah shell | Tidak | Manifest tidak dieksekusi sebagai kode |
| Memanggil API GET/POST kustom atau membuat algoritma autentikasi baru | Tidak melalui field manifest saat ini | Perlu kemampuan runtime baru |
| Membuat/memperbarui token login atau melewati DRM/paywall | Tidak | Sesi sah harus diperoleh lewat alur situs yang tersedia |
| Hardsub, encode ulang, atau konversi format dengan FFmpeg | Tidak melalui plugin | Perlu fitur pemrosesan media terpisah |

**Menemukan link bukan bukti download berhasil.** Masa berlaku token, sesi, manifest, codec, enkripsi, dan format segmen tetap menentukan hasilnya.

## Bedakan plugin dari kemampuan engine

Plugin mengisi aturan untuk kemampuan yang sudah ada. Ia tidak menambahkan implementasi protokol baru.

- HLS ditangani engine bawaan. Jangan menjanjikan semua variasi HLS/enkripsi/live dapat diekspor hanya karena URL terdeteksi.
- Ekspor DASH saat ini berfokus pada **VOD statis, satu Period, representasi MP4 yang didukung**, termasuk jalur AVC/HEVC dan audio AAC yang sudah diuji. Live DASH, multi-period, dan sumber DRM tidak menjadi didukung hanya dengan plugin baru.
- Audio dan subtitle yang menjadi bagian video diproses oleh engine; plugin bukan encoder atau muxer.
- Format akhir file ditentukan engine. Mengganti ekstensi `.ts` menjadi `.mp4` tidak melakukan konversi.
- Subtitle Indonesia diprioritaskan oleh aplikasi ketika tersedia. Pemetaan `in_id` ke `id` dilakukan normalizer aplikasi.
- Subtitle offline otomatis terutama berkaitan dengan bundle video/subtitle yang diunduh dan dicatat YourSafe. Jangan menjanjikan semua pasangan file eksternal terdeteksi dalam semua keadaan.
- Fitur Media Downloader untuk platform lain adalah modul aplikasi tersendiri; jangan menganggap setiap kemampuan modul itu otomatis menjadi field manifest situs.

## Struktur plugin baru

Lokasi: `plugins/<id>/plugin.json`. Contoh berikut hanya dokumentasi; domain dummy tidak boleh dipublikasikan sebagai plugin situs sungguhan.

```json
{
  "apiVersion": 1,
  "id": "example-site",
  "name": "Example Video",
  "description": "Deteksi video dan subtitle dari player situs.",
  "domains": ["video.example"],
  "mediaSelectors": ["video", "video source"],
  "subtitles": {
    "urlKeys": ["subtitleLink", "url"],
    "languageKeys": ["lan", "language"],
    "labelKeys": ["lanName", "label"],
    "containers": ["captions", "subtitles"]
  }
}
```

`version` boleh tidak diisi pada draft baru: bot menambahkannya sebelum aplikasi mengambil plugin. File yang diterima runtime tetap harus memiliki versi integer positif. Jangan menyisipkan komentar dalam JSON.

### Field dasar

| Field | Makna dan batas |
| --- | --- |
| `apiVersion` | Harus `1` untuk runtime saat ini |
| `id` | Pola `[a-z0-9][a-z0-9-]{0,63}`, sama dengan folder; identitas permanen plugin |
| `name` | Nama situs yang tampil, 1–100 karakter |
| `description` | Penjelasan singkat untuk pengguna; bukan kode |
| `version` | Dikelola otomatis; jangan menaikkannya secara manual |
| `domains` | 1–128 hostname lowercase tanpa skema/path; cocok pada hostname tersebut dan subdomainnya |

Contoh: `video.example` cocok dengan `watch.video.example`, tetapi tidak dengan `video.example.evil.test`. Untuk ekstraksi DOM/JSON, domain yang diperiksa adalah **domain dokumen browser yang menjalankan detektor**, bukan otomatis domain server respons API. Jika player berjalan di iframe lain, identifikasi domain dokumen iframe itu dari bukti nyata.

### `mediaSelectors`

Daftar selector CSS, maksimal 16 selector, masing-masing 1–200 karakter. Mesin membaca kandidat berurutan dari `currentSrc`, `src`, `data-src`, lalu atribut `src`, dan menyelesaikan URL relatif terhadap halaman.

Ada batas penting: kandidat masih melewati detektor URL media bawaan. Menunjuk elemen dengan selector tidak menjadikan setiap URL arbitrer sebagai video. `blob:` bukan link unduhan jaringan yang bisa disimpan langsung. Selector juga tidak menekan tombol Play/login, menjalankan ekspresi, atau mengambil atribut lain secara bebas.

Jika link ada di atribut yang belum didukung, atau harus dihitung dengan JavaScript khusus situs, manifest saja belum cukup.

### `subtitles`

| Field | Makna |
| --- | --- |
| `urlKeys` | Urutan nama field string untuk URL subtitle |
| `languageKeys` | Nama field bahasa, misalnya `lan` atau `language` |
| `labelKeys` | Nama field label yang terlihat, misalnya `lanName` |
| `containers` | Nama properti yang menandai kumpulan subtitle, termasuk URL tanpa ekstensi |

Ini adalah **nama field**, bukan JSONPath, regex, fungsi, atau path bertitik. Contoh `data.captions` tidak berarti mesin melakukan traversal JSONPath. Mesin sudah menelusuri objek/array bertingkat dan mengenali nama container pada tiap tingkat. Setiap nama field memakai pola `[A-Za-z0-9_-]{1,60}`.

Pemetaan kustom digabung dengan nama field umum. Mesin juga membaca track DOM, MIME dan URL subtitle yang dikenal. Format yang dikenali mencakup VTT, SRT, ASS/SSA, dan TTML/DFXP sesuai normalisasi/dukungan engine. Batas ukuran, kedalaman traversal dan jumlah track tetap berlaku; bukan seluruh respons API tanpa batas.

Plugin tidak memanggil endpoint subtitle secara mandiri. Respons harus terlihat melalui aktivitas situs yang diamati. Jangan menambahkan URL endpoint atau kunci `fetch` yang tidak memiliki implementasi runtime.

### `playback`

Opsional, khusus pola penerusan token query HLS dan pengenalan playlist tersamar. Berikut contoh **nilai objek `playback`**, bukan manifest lengkap:

```json
{
  "hosts": ["media.video.example", "cdn.video.example"],
  "pathPrefix": "/v/",
  "scopeSegments": 3,
  "tokenParameter": "t",
  "query": {"pm": "browser"},
  "playlistPrefix": "config-",
  "variantPrefix": "data-"
}
```

- `hosts` adalah hostname **eksak**. Tidak menerima wildcard atau otomatis mewarisi pencocokan subdomain dari `domains`.
- Sumber dan target harus HTTPS port 443 tanpa userinfo dalam URL.
- `pathPrefix` berbentuk `/nama/`, dengan nama alfanumerik, `_`, atau `-`.
- `scopeSegments` antara 2 dan 6. Target harus memiliki segmen awal yang sama dengan sumber. Untuk `/v/zone/video/...` dan nilai `3`, token tidak boleh diteruskan ke video lain.
- `tokenParameter` menunjuk token yang **sudah ada** pada URL sumber, bukan membuat token baru. Nama parameter 1–40 karakter alfanumerik/`_`/`-`.
- `query` menambahkan nilai query tetap yang memang diperlukan protokol. Maksimal 16 pasangan, panjang nilai maksimal 256 karakter; nama parameter tidak boleh sama dengan `tokenParameter`.
- `playlistPrefix` dan `variantPrefix` mengenali nama seperti `config-1.json` dan `data-1.json`; keduanya berupa prefix sederhana, bukan regex bebas. Nama yang dikenali memakai suffix alfanumerik/`_`/`-` dan `.json`.
- Cookie, Authorization, header kustom, atau proses redeem tidak bisa didefinisikan dengan menambahkan field manifest baru. Mesin memakai konteks request/sesi browser yang memang berhasil diperoleh.

Jangan memperluas daftar host tanpa bukti kebutuhan media tersebut. Jangan menyimpan token, signed URL aktif, atau kredensial sebagai nilai tetap. Token kedaluwarsa biasanya memerlukan pembaruan sesi melalui player situs, bukan penambahan versi plugin kosong.

## Penambahan yang tidak bekerja hanya dengan JSON

Field seperti `script`, `entrypoint`, `fetch`, `headers`, `login`, `decrypt`, `videoUrlKeys`, `search`, `episodes`, `poster`, `downloadPath`, dan `ffmpeg` **bukan fitur API 1**. Jangan mengarang schema untuk fitur itu. JSON yang berhasil diparse atau berhasil dibuat katalognya belum tentu field-nya dipakai aplikasi.

Jika situs butuh salah satu kemampuan tersebut, jelaskan bagian runtime yang harus diubah. Update APK diperlukan untuk memperkenalkan kemampuan baru; pembaruan JSON hanya cukup jika operasi yang dibutuhkan sudah didukung.

## Publikasi dan sinkronisasi otomatis

1. Tambahkan/edit `plugins/<id>/plugin.json`, kemudian commit ke `main`.
2. Workflow membandingkan isi dengan snapshot publikasi bot terakhir. Perubahan isi menaikkan versi satu angka; plugin baru mulai dari 1. Perubahan whitespace/urutan key atau field versi saja tidak menaikkan versi.
3. Bot menerbitkan versi manifest, `index.json`, dan SHA-256 yang sesuai dalam satu commit. Jangan mengedit katalog/versi secara manual.
4. Pada YourSafe 3.9.3+, saat aplikasi masuk foreground, plugin baru dipasang dan versi baru diperbarui di latar belakang. Tidak perlu token pengguna atau update APK untuk aturan API yang sudah didukung.
5. Ada cooldown lima menit per proses setelah cek berhasil. Kegagalan dapat dicoba lagi setelah satu menit pada pembukaan berikutnya. Cache distribusi juga bisa menunda terlihatnya commit terbaru.
6. Plugin yang sengaja dihapus tetap dikecualikan hingga dipasang kembali secara manual. Menghapus manifest dari repo tidak otomatis menghapus file plugin yang sudah terpasang di perangkat.
7. File plugin/katalog dibatasi ukurannya; runtime membatasi setiap file hingga 512 KiB dan katalog hingga 200 entri. Validasi ID/versi/schema/checksum dilakukan sebelum pemasangan. Versi gagal tidak menggantikan plugin lama.
8. Aturan baru dikirim ke tab browser yang ada. Metadata yang sudah terambil sebelumnya mungkin tetap perlu refresh halaman. Unduhan yang sedang berjalan mempertahankan snapshot aturan sesinya.

## Cara AI menilai situs baru

1. Dapatkan contoh halaman yang benar-benar digunakan. Catat domain dokumen utama dan iframe player.
2. Identifikasi apakah sumbernya MP4, HLS, atau DASH; bedakan master playlist, variant playlist, segmen, key, thumbnail dan iklan.
3. Amati DOM serta respons API yang memang diambil situs. Catat nama field subtitle dan bahasa, tanpa mempublikasikan rahasia sesi.
4. Periksa dulu apakah detektor umum sudah bekerja. Buat aturan tambahan hanya untuk perbedaan yang sudah diketahui.
5. Jika dibutuhkan, pastikan token query HLS memang mengikuti pola scope/host yang didukung. Jangan memakai aturan IDLIX pada situs lain hanya karena sama-sama HLS.
6. Buat manifest minimal. Uji kecocokan domain yang benar dan penolakan domain mirip, selector, subtitle, URL bertoken, serta target video berbeda.
7. Uji Play, download, audio, dan subtitle secara terpisah. Untuk klaim offline, putuskan akses server setelah unduhan dan periksa file lokal.
8. Laporkan bukti dan batas pengujian. Jika hanya memvalidasi JSON atau simulasi, jangan menulis “sudah berhasil di HP”.

## Referensi implementasi

Jika tersedia checkout aplikasi di sebelah repo ini, gunakan `../YourSafeVPN/app/src/main/java/com/yoursafe/vpn/` sebagai acuan:

| File | Tanggung jawab |
| --- | --- |
| `plugins/SitePlugin.kt` | Schema, batas validasi, runtime plugin |
| `plugins/PluginRepository.kt` | Katalog, checksum, pemasangan, preferensi penghapusan |
| `plugins/PluginAutoUpdater.kt` | Pemeriksaan saat foreground dan cooldown |
| `browser/VideoSniffer.kt` | Script deteksi umum, selector dan pemetaan JSON subtitle |
| `browser/PentosPlaybackSession.kt` | Mesin generik aturan `playback`, meskipun nama kelas berasal dari implementasi awal |
| `browser/SubtitleDiscovery.kt` | Normalisasi bahasa/format dan prioritas subtitle |
| `download/HlsHttpSession.kt` | Sesi HTTP untuk media |
| `download/YourSafeDownloadEngine.kt` | Unduhan dan ekspor file |
| `download/DashVodDownload.kt` | Batas dukungan ekspor DASH |

Repo plugin sendiri menyediakan contoh nyata di `plugins/idlix/plugin.json` dan `plugins/moviebox/plugin.json`, generator di `tools/build_index.py`, serta workflow di `.github/workflows/update-index.yml`. Jika kode aplikasi tidak tersedia, tandai ketidakpastian dan jangan menganggap dokumentasi ini memberi runtime kemampuan tambahan.
