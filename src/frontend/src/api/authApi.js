import API from "./apiClient";
import { setTokens, clearTokens } from "./tokenStorage";

export async function register({ username, email, password }) {
  const res = await API.post("/api/auth/register", { username, email, password });
  setTokens(res.data);
  return res.data;
}

export async function login({ login, password }) {
  const res = await API.post("/api/auth/login", { login, password });
  setTokens(res.data);
  return res.data;
}

export async function logout() {
  // endpoint backend protégé
  await API.post("/api/users/logout");
  clearTokens();
}
