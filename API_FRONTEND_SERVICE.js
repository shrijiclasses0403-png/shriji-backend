// src/services/api.js
// Drop this file into your shriji-classes/src/services/ folder

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// ── Token helpers ─────────────────────────────────────────────────────────────
export const getToken  = ()        => localStorage.getItem("shriji_token");
export const setToken  = (token)   => localStorage.setItem("shriji_token", token);
export const clearToken = ()       => localStorage.removeItem("shriji_token");

// ── Base fetch with auth header ───────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    window.location.href = "/";
    return;
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authAPI = {
  adminLogin:  (username, password) =>
    apiFetch("/auth/admin/login", { method: "POST", body: JSON.stringify({ username, password }) }),

  sendOTP:     (phone) =>
    apiFetch("/auth/parent/send-otp", { method: "POST", body: JSON.stringify({ phone }) }),

  verifyOTP:   (phone, otp) =>
    apiFetch("/auth/parent/verify-otp", { method: "POST", body: JSON.stringify({ phone, otp }) }),
};

// ── Students ──────────────────────────────────────────────────────────────────
export const studentsAPI = {
  list:   (params = {}) => apiFetch("/students/?" + new URLSearchParams(params)),
  get:    (id)          => apiFetch(`/students/${id}`),
  create: (data)        => apiFetch("/students/",    { method: "POST", body: JSON.stringify(data) }),
  update: (id, data)    => apiFetch(`/students/${id}`, { method: "PUT",  body: JSON.stringify(data) }),
  delete: (id)          => apiFetch(`/students/${id}`, { method: "DELETE" }),
};

// ── Fees ──────────────────────────────────────────────────────────────────────
export const feesAPI = {
  list:     (params = {}) => apiFetch("/fees/?" + new URLSearchParams(params)),
  create:   (data)        => apiFetch("/fees/",  { method: "POST",  body: JSON.stringify(data) }),
  markPaid: (id, data)    => apiFetch(`/fees/${id}/mark-paid`, { method: "PATCH", body: JSON.stringify(data) }),
  delete:   (id)          => apiFetch(`/fees/${id}`, { method: "DELETE" }),
};

// ── Marks ─────────────────────────────────────────────────────────────────────
export const marksAPI = {
  list:   (params = {}) => apiFetch("/marks/?" + new URLSearchParams(params)),
  create: (data)        => apiFetch("/marks/",    { method: "POST",   body: JSON.stringify(data) }),
  update: (id, data)    => apiFetch(`/marks/${id}`, { method: "PUT",  body: JSON.stringify(data) }),
  delete: (id)          => apiFetch(`/marks/${id}`, { method: "DELETE" }),
};

// ── Attendance ────────────────────────────────────────────────────────────────
export const attendanceAPI = {
  list:   (params = {}) => apiFetch("/attendance/?" + new URLSearchParams(params)),
  upsert: (data)        => apiFetch("/attendance/upsert", { method: "POST", body: JSON.stringify(data) }),
};

// ── Notes ─────────────────────────────────────────────────────────────────────
export const notesAPI = {
  list:   (params = {}) => apiFetch("/notes/?" + new URLSearchParams(params)),

  upload: (formData) => {
    const token = getToken();
    return fetch(`${BASE_URL}/notes/`, {
      method:  "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body:    formData,   // FormData for file upload — no Content-Type header!
    }).then(r => r.json());
  },

  downloadURL: (noteId) => `${BASE_URL}/notes/${noteId}/download?token=${getToken()}`,
  delete:      (id)     => apiFetch(`/notes/${id}`, { method: "DELETE" }),
};
