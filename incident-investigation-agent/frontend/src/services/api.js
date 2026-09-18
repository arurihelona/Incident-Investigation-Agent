const API_BASE = '/api';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function getDocuments() {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(`Fetch documents failed: ${res.statusText}`);
  return res.json();
}

export async function reindexDocuments() {
  const res = await fetch(`${API_BASE}/reindex`, { method: 'POST' });
  if (!res.ok) throw new Error(`Reindexing failed: ${res.statusText}`);
  return res.json();
}

export async function runInvestigation(question) {
  const res = await fetch(`${API_BASE}/investigate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Investigation failed: ${res.statusText}`);
  }
  return res.json();
}
