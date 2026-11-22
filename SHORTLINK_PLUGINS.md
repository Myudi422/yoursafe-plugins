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

## Modul awal yang diadaptasi

| Plugin | Sumber pola | Cakupan aktual |
| --- | --- | --- |
| `shortlink-linkvertise` | Cabang lokal `r` pada `extra_bypasses/apis.user.js` | Decode parameter base64 `r`, lalu validasi tujuan HTTPS. Kasus yang memerlukan resolver/server eksternal tidak didukung. |
| `shortlink-acortalink` | Selector `a.button#contador` pada `extra_bypasses/acortalink.user.js` | Membuka URL pada anchor yang sudah tersedia. Tidak menyalin spoofing `postMessage`, manipulasi popup, CAPTCHA, atau algoritma verifikasi upstream. |

Provenance dan batas adaptasi ada di `attribution` setiap manifest serta [THIRD_PARTY.md](THIRD_PARTY.md). Ini bukan port semua domain/fitur repo upstream. Jangan menambahkan manifest domain yang belum diamati atau menjanjikan shortlink terproteksi selesai hanya karena halaman cocok.

## Pengujian dan perubahan kemampuan

Generator mendukung API 1/video dan API 2/shortlink. Untuk generator/workflow jalankan `python -m unittest discover -s tools -p 'test_*.py'`. Runtime aplikasi memiliki tes untuk akses Java yang ditolak, loop, input/output besar, scope terpisah, validasi URL, pembatasan rantai, auto install dan kedua modul contoh.

Tes JVM/simulasi tidak membuktikan binder, UID isolasi atau situs live berhasil di perangkat. Pengujian perangkat nyata harus memeriksa proses `:shortlink_sandbox`, navigasi saat tab berubah, kematian worker dan alur situs dengan sesi yang valid. Jangan menyatakan cakupan 400+ domain atau semua kasus situs berdasarkan dua modul awal ini.

Jika membutuhkan API jaringan, UI deklaratif, storage plugin, collector tambahan atau aksi submit/click, definisikan dan implementasikan kemampuan runtime baru beserta validasi dan pengujiannya terlebih dahulu. Jangan menambahkan permission/field yang belum dilayani aplikasi.
