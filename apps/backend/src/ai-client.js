export const CLASSES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferative_DR'];
export class ApiError extends Error {
  constructor(status, code, message) { super(message); this.status = status; this.code = code; }
}
export async function predict(config, buffer, mime) {
  const body = new FormData();
  body.append('image', new Blob([buffer], { type: mime }), mime === 'image/png' ? 'fundus.png' : 'fundus.jpg');
  let response, result;
  try {
    response = await fetch(`${config.aiUrl}/predict`, { method: 'POST', body, signal: AbortSignal.timeout(config.aiTimeout) });
    result = await response.json();
  } catch (error) {
    throw new ApiError(502, error.name === 'TimeoutError' ? 'AI_TIMEOUT' : 'AI_UNAVAILABLE', 'AI service could not complete the request.');
  }
  if (!response.ok) throw new ApiError(502, 'INFERENCE_FAILED', 'AI service rejected the request.');
  const p = result.probabilities;
  const index = CLASSES.indexOf(result.prediction?.class);
  if (result.success !== true || index < 0 || !p || Object.keys(p).length !== 5 ||
      !CLASSES.every(c => Number.isFinite(p[c]) && p[c] >= 0 && p[c] <= 1) ||
      Math.abs(CLASSES.reduce((sum, c) => sum + p[c], 0) - 1) > 0.0001 ||
      result.prediction.confidence !== p[CLASSES[index]] || p[CLASSES[index]] !== Math.max(...Object.values(p)) ||
      !['LOW', 'MEDIUM', 'HIGH'].includes(result.riskLevel) ||
      typeof result.modelVersion !== 'string' || !result.modelVersion || typeof result.isMock !== 'boolean') {
    throw new ApiError(502, 'INVALID_AI_RESPONSE', 'AI response does not match the contract.');
  }
  return { predictedClass: result.prediction.class, confidence: result.prediction.confidence,
    probabilities: p, riskLevel: result.riskLevel, modelVersion: result.modelVersion, isMock: result.isMock };
}
