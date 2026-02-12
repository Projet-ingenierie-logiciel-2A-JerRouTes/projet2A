import API from "./apiClient";
import { setTokens, clearTokens } from "./tokenStorage";

/**
 * Connexion utilisateur
 * @param {Object} credentials - Doit contenir { pseudo, password }
 */
export async function login(credentials) {
  // Envoie les données vers la route POST /api/auth/login
  const res = await API.post("/api/auth/login", credentials);

  // On stocke les données de l'utilisateur (ou tokens) si présents
  if (res.data) {
    setTokens(res.data);
  }
  return res.data;
}

/**
 * Création de compte
 * @param {Object} userData - Contient { pseudo, email, password }
 */

export async function register(payload) {
  // On envoie le payload directement, il est déjà au bon format
  const res = await API.post("/api/auth/register", payload);
  return res.data;
}

/**
 * Récupération de tous les utilisateurs (pour test/admin)
 */
export async function getAllUsers() {
  const res = await API.get("/api/auth/users");
  return res.data;
}

/**
 * Déconnexion
 */
export async function logout() {
  // On nettoie le stockage local (tokens/infos user)
  clearTokens();
  // Optionnel : appel au backend si vous créez une route logout plus tard
}
