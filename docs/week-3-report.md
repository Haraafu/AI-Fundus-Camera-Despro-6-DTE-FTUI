# Laporan Pekan 3 — Backend Foundation & Mock AI Integration

Tanggal verifikasi: 12 September 2026. Acuan jadwal: Weekly_Planner_Software_Despro2_Final.md bagian B. PRD tetap menjadi acuan arsitektur; target dataset pada jadwal PRD awal telah digantikan planner terbaru karena dataset/preprocessing tersedia dan model dikerjakan anggota lain.

## Luaran implementasi

| Target | Bukti |
| --- | --- |
| Struktur repository | apps/backend, apps/frontend, services/ai-service, docs, scripts |
| Backend Node/Express | apps/backend/src/server.js, empat endpoint sesuai planner |
| Service Python terpisah | services/ai-service/app.py, /health dan /predict |
| Kontrak API | docs/api.md; validasi respons AI di ai-client.js |
| Upload citra | multipart PNG/JPEG, decode validation, pembatasan ukuran, penyimpanan byte original |
| Mock prediction | Moderate, confidence 0.81, lima probabilitas, MEDIUM, mock-v0, isMock=true |
| Examination status | CREATED → IMAGE_RECEIVED → PROCESSING → COMPLETED; FAILED jika proses gagal |
| Schema database | Patient, Examination, FundusImage, AIResult melalui SQLite lokal |
| Environment | .env.example, path lokal, timeout, ukuran upload, host/port |
| Dokumentasi menjalankan | README.md, scripts/smoke.mjs |

## Hasil pengujian

Windows, Node 24.18.0, Python 3.11.9. `npm test`: **6 tes lulus, 0 gagal**.

1. Health kedua service, upload HTTP ke Python sungguhan, respons mock, urutan status, keutuhan byte original, pembacaan ulang database, penolakan upload ulang.
2. Metadata tidak valid, ID tidak dikenal, file hilang, isi file palsu, MIME salah, metadata eye tidak cocok, ukuran berlebih; pemeriksaan tetap CREATED untuk input ditolak.
3. AI tidak tersedia → HTTP 502, FAILED tersimpan, original tetap ada.
4. Timeout dan respons AI tidak sesuai kontrak → FAILED, tidak menghasilkan hasil sukses palsu.
5. Dua upload bersamaan → satu sukses, satu 409.
6. Python menolak file rusak melalui /predict langsung.

Smoke test terpisah menjalankan entrypoint kedua service, menggunakan citra dataset `colored_images/Mild/0024cdab0c1e.png` (224×224, 65.614 byte), lalu script client membuat examination, upload, dan GET hasil. Examination `f604eb7d-7626-4b85-932b-9f01d607269c` mencapai COMPLETED; hasil mock-v0/isMock=true; error null. Waktu createdAt–completedAt sekitar 103 ms pada satu percobaan mock, bukan benchmark model aktual. Service pengujian dihentikan setelah selesai; hasil demo tersimpan lokal di data/ yang diabaikan Git.

`npm install` setelah pembaruan sharp 0.35.4: audit 0 vulnerabilities. `pip check`: no broken requirements. `git diff --check`: tidak ada error whitespace (hanya pemberitahuan konversi LF/CRLF).

## Batasan dan handoff pekan 4

Mock tidak memuat model, tidak mengukur akurasi, dan memberikan nilai yang sama untuk semua citra valid. Belum ada preprocessing aktual, quality gate fundus/blur/exposure, Grad-CAM, dashboard, MQTT, atau PDF. HTTP loopback dan database lokal untuk development; satu instance backend per database.

Pekan 4: masukkan adapter EfficientNetB3 pada service Python, hubungkan preprocessing existing, keluarkan lima probabilitas dengan label kanonis kontrak, gunakan isMock=false dan versi model aktual, lalu ulangi tes integrasi. Jangan menyamakan nama folder legacy Proliferate_DR dengan urutan kelas model tanpa memeriksa mapping training.
