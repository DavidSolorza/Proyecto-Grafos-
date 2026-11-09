/**
 * Native REST API client connecting to Flask backend.
 */
const API_BASE_URL = 'http://localhost:5000/api';

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
    return await res.json();
  } catch (error) {
    return { status: 'disconnected', error: error.message };
  }
}

export async function fetchCurrentScenario() {
  const res = await fetch(`${API_BASE_URL}/scenario/current`);
  if (!res.ok) throw new Error(`Error fetching scenario: ${res.status}`);
  return await res.json();
}

export async function uploadScenarioFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/scenario/upload`, {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  if (!res.ok || !data.success) {
    throw new Error(data.error || 'Failed to upload scenario');
  }
  return data;
}
