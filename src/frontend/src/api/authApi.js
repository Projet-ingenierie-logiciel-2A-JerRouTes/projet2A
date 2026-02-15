import API from "./apiClient";
import { setTokens, clearTokens } from "./tokenStorage";

/**
 * Connexion utilisateur
 * @param {Object} credentials - Doit contenir { pseudo, password }
 */
export async function login_v2(credentials) {
  // Envoie : { login_v2: "pseudo", password: "..." }
  const res = await API.post("/api/auth/login_v2", credentials);

  if (res.data) {
    // On stocke les tokens
    setTokens(res.data);

    // Si ton backend ne renvoie PAS encore le profil complet au login,
    // tu peux faire un appel immédiat vers /api/users/me
    const profileRes = await API.get("/api/users/me");

    // On fusionne les tokens et les infos de profil (pseudo, id_stock, role)
    return { ...res.data, user: profileRes.data.user };
  }
  return res.data;
}

/**
 * Connexion utilisateur
 * @param {Object} credentials - Contient { login, password }
 * @param {boolean} is_admin - Si true, ajoute ?admin=true à la requête pour le backend
 */
export async function login(credentials, is_admin = false) {
  // Construction dynamique de l'URL avec le Query Parameter 'admin'
  // Si is_admin est vrai, l'URL devient /api/auth/login?admin=true
  const url = is_admin ? "/api/auth/login?admin=true" : "/api/auth/login";

  // Envoi de la requête POST au backend
  const res = await API.post(url, credentials);

  if (res.data) {
    // Stockage des tokens (access et refresh)
    setTokens(res.data);

    // Récupération immédiate du profil complet (pseudo, rôle, etc.)
    const profileRes = await API.get("/api/users/me");

    // Fusion des tokens et des informations utilisateur pour le state global
    return {
      ...res.data,
      user: profileRes.data.user,
    };
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
