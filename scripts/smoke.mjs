import { readFile } from 'node:fs/promises';
const [imagePath, base = 'http://127.0.0.1:3001'] = process.argv.slice(2);
if (!imagePath) throw new Error('Usage: npm run smoke -- path/to/fundus.png [backend URL]');
async function request(path, options) {
  const response = await fetch(base + path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(JSON.stringify(body));
  return body;
}
console.log(await request('/health'));
const exam = await request('/api/examinations', { method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ patientId: 'DEMO-001', eye: 'RIGHT', captureType: 'MACULA_CENTERED' }) });
const form = new FormData();
form.append('image', new Blob([await readFile(imagePath)], { type: /\.png$/i.test(imagePath) ? 'image/png' : 'image/jpeg' }), 'fundus' + (/\.png$/i.test(imagePath) ? '.png' : '.jpg'));
const result = await request(`/api/examinations/${exam.examinationId}/images`, { method: 'POST', body: form });
if (result.status !== 'COMPLETED' || result.result.isMock !== true) throw new Error('Unexpected mock result');
console.log(JSON.stringify(await request(`/api/examinations/${exam.examinationId}`), null, 2));
