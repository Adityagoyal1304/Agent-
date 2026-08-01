// api.js — Fetch and EventSource wrappers for PixelForge backend
//
// With Vite's proxy config, '/api' requests are forwarded to localhost:8000.
// In production, set VITE_API_URL to the backend's public URL.

const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Upload a target image and get a run_id back.
 * @param {File} file
 * @returns {Promise<{run_id: string}>}
 */
export async function createRun(file) {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${API_BASE}/api/runs`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Failed to create run: ${err}`);
  }
  return res.json();
}

/**
 * Open an EventSource for a run and call onEvent for each SSE message.
 * Returns the EventSource so the caller can close it.
 * @param {string} runId
 * @param {(data: object) => void} onEvent
 * @param {(err: Event) => void} onError
 * @returns {EventSource}
 */
export function streamRun(runId, onEvent, onError) {
  const url = `${API_BASE}/api/runs/${runId}/stream`;
  const es = new EventSource(url);

  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onEvent(data);
      if (data.done) {
        es.close();
      }
    } catch (parseErr) {
      console.error('Failed to parse SSE event:', parseErr);
    }
  };

  es.onerror = (err) => {
    onError(err);
    es.close();
  };

  return es;
}

/**
 * Trigger a file download of best.html for a run.
 * @param {string} runId
 */
export function downloadBest(runId) {
  window.open(`${API_BASE}/api/runs/${runId}/download`, '_blank');
}
