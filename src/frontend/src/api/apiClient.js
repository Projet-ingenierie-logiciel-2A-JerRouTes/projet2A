import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./tokenStorage";

const apiUrl = import.meta.env.VITE_API_URL;

const API = axios.create({
  baseURL: apiUrl,
});

// Ajoute automatiquement Authorization: Bearer <token>
API.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// (Optionnel) refresh automatique si 401
let isRefreshing = false;
let pending = [];

function resolvePending(error, token = null) {
  pending.forEach(({ resolve, reject }) => (error ? reject(error) : resolve(token)));
  pending = [];
}

API.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;

    if (err.response?.status !== 401 || original?._retry) {
      throw err;
    }

    const refresh = getRefreshToken();
    if (!refresh) {
      clearTokens();
      throw err;
    }

    original._retry = true;

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pending.push({
          resolve: (token) => {
            original.headers.Authorization = `Bearer ${token}`;
            resolve(API(original));
          },
          reject,
        });
      });
    }

    isRefreshing = true;

    try {
      const r = await axios.post(`${apiUrl}/api/auth/refresh`, { refresh_token: refresh });
      setTokens(r.data);

      resolvePending(null, r.data.access_token);

      original.headers.Authorization = `Bearer ${r.data.access_token}`;
      return API(original);
    } catch (e) {
      resolvePending(e, null);
      clearTokens();
      throw e;
    } finally {
      isRefreshing = false;
    }
  }
);

export default API;