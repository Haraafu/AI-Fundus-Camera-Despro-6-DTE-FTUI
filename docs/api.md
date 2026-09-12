# Kontrak API pekan 3

Planner final menjadi acuan jadwal; PRD menjadi acuan arsitektur. Endpoint lokal HTTP, loopback secara default. Autentikasi, HTTPS/LAN, model aktual, quality gate klinis, Grad-CAM, dan dashboard ada di tahap berikutnya.

## Backend

`GET /health`: 200 `{ "status": "healthy", "service": "backend" }`. Ini liveness backend, bukan readiness AI.

`POST /api/examinations`: JSON `{"patientId":"DEMO-001","eye":"RIGHT","captureType":"MACULA_CENTERED"}` → 201 examination. patientId adalah kode anonim 1–64 karakter alfanumerik/underscore/dash; Patient minimal otomatis dibuat jika belum ada. Eye LEFT/RIGHT, captureType MACULA_CENTERED/OPTIC_DISC_CENTERED.

`POST /api/examinations/:id/images`: multipart `image` wajib PNG/JPEG, maksimal 10 MiB default; file benar-benar didecode, maksimal 40 juta piksel. Opsional `eye`, `capture_type` harus cocok dengan pemeriksaan; `device_id` kode 1–64 karakter; `capture_timestamp` timestamp yang dapat diparse. Backend menyimpan byte original tanpa perubahan lalu mengirim file multipart ke Python. Respons sinkron 200 examination lengkap setelah inference selesai.

`GET /api/examinations/:id`: 200 examination tersimpan, 404 jika tidak ada.

Status: CREATED → IMAGE_RECEIVED → PROCESSING → COMPLETED/FAILED. Setiap transisi tercatat pada statusHistory. Input tidak valid tetap CREATED; kegagalan AI menjadi FAILED. Satu citra per examination pada pekan 3; upload ulang/bersamaan menghasilkan 409. Buat examination baru untuk retake. Restart mengubah proses yang tertinggal menjadi FAILED/PROCESS_INTERRUPTED.

Examination: examinationId, patientId, eye, captureType, status, createdAt, completedAt (null sampai sukses), image, result, error, statusHistory.

Image: imageId, originalPath (nama file relatif terhadap UPLOAD_DIR), mimeType, sizeBytes, originalResolution, eye, captureType, deviceId, capturedAt, processedPath dan preprocessingVersion (null untuk mock).

Result: predictedClass, confidence, probabilities, riskLevel, modelVersion, isMock. Label kanonis `No_DR`, `Mild`, `Moderate`, `Severe`, `Proliferative_DR`. Folder dataset lama `Proliferate_DR` dipertahankan; adapter model pekan 4 harus memetakan labelnya secara eksplisit.

Error: `{ "success": false, "error": { "code": "...", "message": "..." } }`. Status 400 input tidak valid, 404 tidak ditemukan, 409 examination terkunci, 413 terlalu besar, 502 kegagalan/timeout/kontrak AI tidak valid, 500 internal/storage error. Citra original tetap tersimpan bila inference gagal.

## AI Python

`GET /health`: status healthy, modelLoaded false, modelVersion mock-v0, isMock true.

`POST /predict`: multipart `image` PNG/JPEG. 200:

```json
{
  "success": true,
  "isMock": true,
  "prediction": {"class": "Moderate", "confidence": 0.81},
  "probabilities": {"No_DR": 0.02, "Mild": 0.07, "Moderate": 0.81, "Severe": 0.08, "Proliferative_DR": 0.02},
  "riskLevel": "MEDIUM",
  "modelVersion": "mock-v0"
}
```

Semua citra valid menghasilkan dummy yang sama; tidak ada analisis penyakit atau preprocessing aktual. Python menolak corrupt/format salah (400), file terlalu besar (413), multipart tanpa image (422 validasi FastAPI). Backend menerjemahkan kegagalan service menjadi error 502, tidak meneruskan rincian internal.

## Penyimpanan lokal

SQLite bawaan Node: patients(patientId PK, createdAt), examinations(examinationId PK, patientId FK, document JSON), fundus_images(imageId PK, examinationId FK, document JSON), ai_results(examinationId PK/FK, document JSON). Perubahan entitas disimpan dalam transaksi. Jalankan satu instance backend per database. JSON document memungkinkan perluasan schema pekan 5; migrasi MongoDB belum dikerjakan. File original tidak disajikan sebagai direktori publik.
