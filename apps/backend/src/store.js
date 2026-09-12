import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

export function createStore(path) {
  mkdirSync(dirname(path), { recursive: true });
  const db = new DatabaseSync(path);
  db.exec(`PRAGMA foreign_keys=ON;
    CREATE TABLE IF NOT EXISTS patients (patientId TEXT PRIMARY KEY, createdAt TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS examinations (
      examinationId TEXT PRIMARY KEY, patientId TEXT NOT NULL REFERENCES patients(patientId),
      document TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS fundus_images (
      imageId TEXT PRIMARY KEY, examinationId TEXT NOT NULL REFERENCES examinations(examinationId),
      document TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS ai_results (
      examinationId TEXT PRIMARY KEY REFERENCES examinations(examinationId), document TEXT NOT NULL);`);
  const get = id => {
    const row = db.prepare('SELECT document FROM examinations WHERE examinationId=?').get(id);
    return row ? JSON.parse(row.document) : null;
  };
  function save(exam) {
    db.exec('BEGIN');
    try {
      db.prepare('INSERT OR IGNORE INTO patients VALUES (?,?)').run(exam.patientId, exam.createdAt);
      db.prepare('INSERT INTO examinations VALUES (?,?,?) ON CONFLICT(examinationId) DO UPDATE SET document=excluded.document')
        .run(exam.examinationId, exam.patientId, JSON.stringify(exam));
      if (exam.image) db.prepare('INSERT OR REPLACE INTO fundus_images VALUES (?,?,?)')
        .run(exam.image.imageId, exam.examinationId, JSON.stringify(exam.image));
      if (exam.result) db.prepare('INSERT OR REPLACE INTO ai_results VALUES (?,?)')
        .run(exam.examinationId, JSON.stringify(exam.result));
      db.exec('COMMIT');
    } catch (error) { db.exec('ROLLBACK'); throw error; }
  }
  // A process interrupted during inference cannot complete its old request.
  for (const row of db.prepare('SELECT document FROM examinations').all()) {
    const exam = JSON.parse(row.document);
    if (['IMAGE_RECEIVED', 'PROCESSING'].includes(exam.status)) {
      exam.status = 'FAILED';
      exam.error = { code: 'PROCESS_INTERRUPTED', message: 'Backend restarted during processing.' };
      exam.statusHistory.push({ status: 'FAILED', timestamp: new Date().toISOString() });
      save(exam);
    }
  }
  return { get, save, close: () => db.close() };
}
