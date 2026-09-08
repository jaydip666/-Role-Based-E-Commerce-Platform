import api from "./api";

export const register = (name, email, password) =>
  api.post("/auth/register", { name, email, password }).then((r) => r.data.data);

export const login = (email, password) =>
  api.post("/auth/login", { email, password }).then((r) => r.data.data);

export const getMe = () => api.get("/auth/me").then((r) => r.data.data.user);

export const updateProfile = (updates) => api.put("/auth/me", updates).then((r) => r.data.data.user);
