/**
 * NirikshanX Scan Submission & Polling Module
 */
import { apiFetch } from './api.js';

export async function submitScanForm(formData) {
  return await apiFetch('/scans/submit', {
    method: 'POST',
    body: formData,
  });
}

export async function pollScanResult(scanId, onUpdate, maxAttempts = 30, intervalMs = 1500) {
  let attempts = 0;
  
  return new Promise((resolve, reject) => {
    const timer = setInterval(async () => {
      attempts++;
      try {
        const scan = await apiFetch(`/scans/${scanId}`);
        if (onUpdate) onUpdate(scan);

        const status = scan.status;
        if (status !== 'PENDING' && status !== 'PROCESSING') {
          clearInterval(timer);
          resolve(scan);
        } else if (attempts >= maxAttempts) {
          clearInterval(timer);
          reject(new Error('Scan polling timed out'));
        }
      } catch (err) {
        clearInterval(timer);
        reject(err);
      }
    }, intervalMs);
  });
}

export async function getScanDetails(scanId) {
  return await apiFetch(`/scans/${scanId}`);
}

export async function listUserScans(skip = 0, limit = 20) {
  return await apiFetch(`/scans/?skip=${skip}&limit=${limit}`);
}
