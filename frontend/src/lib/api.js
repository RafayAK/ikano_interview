const API_BASE_URL =
  import.meta.env.PUBLIC_API_BASE_URL !== undefined
    ? import.meta.env.PUBLIC_API_BASE_URL
    : "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include", // send/receive the resume cookie
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(typeof body?.detail === "string" ? body.detail : "Request failed");
    error.status = response.status;
    error.body = body;
    throw error;
  }
  return body;
}

export function createApplication(country, customerType) {
  return request("/applications", {
    method: "POST",
    body: JSON.stringify({ country, customer_type: customerType }),
  });
}

export function getApplication(applicationId) {
  return request(`/applications/${applicationId}`);
}

export function getCurrentStep(applicationId) {
  return request(`/applications/${applicationId}/steps/current`);
}

export function putStep(applicationId, stepId, answers) {
  return request(`/applications/${applicationId}/steps/${stepId}`, {
    method: "PUT",
    body: JSON.stringify(answers),
  });
}

export function submitApplication(applicationId) {
  return request(`/applications/${applicationId}/submit`, { method: "PUT" });
}

export function getAuditEvents(applicationId) {
  return request(`/applications/${applicationId}/audit-events`);
}

export function getResume() {
  return request("/resume");
}

export function clearResume() {
  return request("/resume/clear", { method: "POST" });
}
