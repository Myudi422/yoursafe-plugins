# Provenance dan lisensi

## Aturan shortlink

Referensi: [nOneCode4u/bypass-shortlinks](https://github.com/nOneCode4u/bypass-shortlinks), snapshot `01ad94a99974d3079facb6ec47e562b984af87b7`.

Repo referensi menyertakan [Unlicense](https://github.com/nOneCode4u/bypass-shortlinks/blob/01ad94a99974d3079facb6ec47e562b984af87b7/LICENSE). Provenance setiap manifest menunjuk modul yang menjadi acuan.

- Linkvertise mengadaptasi cabang kecil decoder parameter `r` dari `extra_bypasses/apis.user.js`; tidak memakai jalur resolver eksternal.
- Acortalink memakai fakta selector ready-link `a.button#contador` yang terlihat pada `extra_bypasses/acortalink.user.js`. Implementasi YourSafe hanya membaca href yang sudah tersedia, bukan menyalin routine AdGuard untuk spoofing pesan atau override popup yang terdapat pada modul upstream.

Lisensi repo referensi tidak otomatis menggantikan hak atau lisensi kode pihak ketiga yang tertanam di sana. Pertahankan provenance dan periksa lisensi bagian yang benar-benar diadaptasi saat menambah modul lain. Jangan menyalin script gabungan/obfuscated beserta semua dependensinya tanpa peninjauan.

## Runtime aplikasi

YourSafe menggunakan Mozilla Rhino 1.8.1 (MPL 2.0) tanpa modifikasi sumber Rhino. Sumber resmi tersedia pada tag [Rhino1_8_1_Release](https://github.com/mozilla/rhino/tree/Rhino1_8_1_Release). APK menyertakan teks MPL 2.0 dan catatan runtime dalam assets lisensi. Kode adapter sandbox YourSafe adalah lapisan aplikasi terpisah.
