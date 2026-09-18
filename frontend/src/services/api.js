import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authAPI = {
  signup: (data) => api.post("/api/auth/signup", data),
  login: (data) => api.post("/api/auth/login", data),
};

export const movieAPI = {
  search: (query) => api.get(`/api/movies/search?query=${encodeURIComponent(query)}`),
};

export const journalAPI = {
  create: (data) => api.post("/api/journal", data),
  list: () => api.get("/api/journal"),
  update: (id, data) => api.put(`/api/journal/${id}`, data),
  delete: (id) => api.delete(`/api/journal/${id}`),
};

export const analyticsAPI = {
  overview: () => api.get("/api/analytics/overview"),
  genres: () => api.get("/api/analytics/genres"),
  directors: () => api.get("/api/analytics/directors"),
  timeline: () => api.get("/api/analytics/timeline"),
  summary: () => api.get("/api/analytics/summary"),
};

export const recommendAPI = {
  getRecommendations: (mood, limit = 10) =>
    api.post("/api/recommendations", { mood, limit }),
};

export const friendsAPI = {
  send: (email) => api.post("/api/friends/request", { addressee_email: email }),
  accept: (id) => api.post(`/api/friends/${id}/accept`),
  reject: (id) => api.post(`/api/friends/${id}/reject`),
  list: () => api.get("/api/friends"),
  pending: () => api.get("/api/friends/pending"),
};

export const socialAPI = {
  like: (entryId) => api.post(`/api/social/entries/${entryId}/like`),
  comment: (entryId, text) => api.post(`/api/social/entries/${entryId}/comments`, { text }),
  getComments: (entryId) => api.get(`/api/social/entries/${entryId}/comments`),
  publicJournal: (userId) => api.get(`/api/social/users/${userId}/journal`),
};

export const compareAPI = {
  compare: (otherUserId) => api.get(`/api/compare/${otherUserId}`),
};

export default api;
