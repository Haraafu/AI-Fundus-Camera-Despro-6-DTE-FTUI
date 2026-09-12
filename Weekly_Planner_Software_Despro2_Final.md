# Weekly Planner Software Despro 2

**Project:** Perancangan dan Implementasi Sistem Kamera Fundus Berbasis AI untuk Deteksi Multi-Penyakit dengan 9 Kategori Risiko Kesehatan  
**Fokus:** Sisi Software  
**Periode:** Pekan 2 sampai 28 Oktober 2026  
**Target akhir:** Pada 28 Oktober 2026, sistem software sudah terintegrasi dengan hardware dan siap diuji secara end-to-end.

## Asumsi Dasar

- Dataset sudah diperoleh sejak Despro 1.
- Pipeline preprocessing sudah berjalan dengan baik.
- Training ulang EfficientNetB3 untuk mengurangi overfitting sedang dikerjakan paralel oleh anggota tim lain.
- Model EfficientNetB3 final ditargetkan tersedia pada pekan berikutnya.
- Backend Despro 2 dijalankan secara lokal.
- Source code disimpan di GitHub agar mudah dipindahkan dan dijalankan di perangkat lain.
- Integrasi hardware dilakukan melalui jaringan lokal/LAN, bukan cloud.
- Fokus awal dipercepat agar Oktober lebih banyak digunakan untuk integrasi, debugging, dan stabilisasi.

---

# A. Weekly Planner Software

| Pekan | Periode | Fokus | Pekerjaan Utama | Target Luaran |
|---|---|---|---|---|
| **Pekan 2** | **31 Agustus - 5 September 2026** | **Development Environment & Repository Setup** | Install VS Code dan Git; setup repository GitHub; import kode preprocessing Despro 1; review kembali arsitektur software; memastikan environment lokal siap digunakan | Repository aktif; Git dan VS Code siap; preprocessing tersedia di repository |
| **Pekan 3** | **7 - 12 September 2026** | **Backend Foundation & Mock AI Integration** | Merapikan struktur repository; membuat backend Node.js + Express; membuat struktur AI service; menentukan kontrak API antara backend dan AI; membuat endpoint upload citra; membuat mock/dummy AI response; membuat struktur status examination; menyiapkan `.env.example`; mulai schema database lokal/terhubung | Backend dapat menerima citra dan menjalankan alur awal menggunakan mock AI tanpa menunggu model EfficientNetB3 final |
| **Pekan 4** | **14 - 19 September 2026** | **Integrasi EfficientNetB3 Final** | Memasukkan model EfficientNetB3 final; menghubungkan preprocessing existing dengan model; implement inference aktual; menyimpan probability per class; model versioning; error handling; menghubungkan output AI ke backend | Image dapat dikirim ke backend lalu diproses oleh EfficientNetB3 final dan menghasilkan prediction aktual |
| **Pekan 5** | **21 - 26 September 2026** | **Database, Risk Scoring, dan Grad-CAM** | Menyimpan original image, processed image, prediction, confidence, dan metadata pemeriksaan; implement risk-scoring; implement Grad-CAM; membuat endpoint result; merapikan struktur patient dan examination | Pipeline AI v1 lengkap: image → preprocessing → prediction → confidence → risk → Grad-CAM → database |
| **Pekan 6** | **28 September - 3 Oktober 2026** | **Frontend Minimum Viable Product** | Membuat dashboard Next.js; halaman patient; halaman examination; halaman result; menampilkan original image, processed image, prediction, confidence, risk level, dan Grad-CAM; menampilkan status processing/error | Full software MVP dapat digunakan tanpa hardware fisik |
| **Pekan 7** | **5 - 10 Oktober 2026** | **PDF Reporting & Hardware Interface Preparation** | Implement laporan PDF; menentukan format request hardware; endpoint upload khusus ESP32; menentukan device ID dan metadata; menentukan MQTT topic/status; membuat mock ESP32 client dari laptop | Backend siap menerima hardware; mock ESP32 dapat mengirim citra dan status ke sistem |
| **Pekan 8** | **12 - 17 Oktober 2026** | **Local Network & Device Communication Testing** | Menjalankan backend di laptop lokal menggunakan IP LAN; testing request dari perangkat lain; implement MQTT backend; testing status `IDLE`, `READY`, `CAPTURING`, `UPLOADING`, `ERROR`; timeout dan retry handling; pengujian multipart upload | Mock hardware → backend lokal → AI → database → dashboard → PDF berjalan end-to-end |
| **Pekan 9** | **19 - 24 Oktober 2026** | **Integrasi Hardware Asli** | Menghubungkan ESP32/fundus camera asli ke backend melalui Wi-Fi/LAN; uji image upload; sinkronisasi metadata; debugging network, format image, timeout, ukuran file, dan memory; repeated capture testing | Hardware asli berhasil mengirim citra hingga hasil tampil pada dashboard |
| **Pekan 10** | **26 - 28 Oktober 2026** | **Stabilization, Bug Fixing, dan Demo Freeze** | Full end-to-end testing; perbaikan bug terakhir; latency measurement; validasi error handling; logging; pengecekan repository; dokumentasi cara menjalankan sistem di device lain; freeze versi demo | **28 Oktober 2026: software stabil, terintegrasi dengan hardware, dapat dijalankan secara lokal, dan siap demo** |

---

## Milestone Internal

Agar proyek tidak mepet, target internal ditetapkan lebih awal dari deadline akhir.

| Deadline | Milestone |
|---|---|
| **12 September 2026** | Backend dasar + mock AI berjalan |
| **19 September 2026** | EfficientNetB3 final sudah terintegrasi |
| **26 September 2026** | AI pipeline lengkap + Grad-CAM + database |
| **3 Oktober 2026** | Full software MVP berjalan tanpa hardware |
| **10 Oktober 2026** | PDF + hardware API + mock device siap |
| **17 Oktober 2026** | Simulasi hardware melalui LAN berhasil end-to-end |
| **24 Oktober 2026** | Hardware asli sudah terintegrasi |
| **28 Oktober 2026** | Stabilization dan demo-ready |
---

