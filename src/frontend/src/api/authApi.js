import API from "./apiClient";
import { setTokens, clearTokens } from "./tokenStorage";

/**
 * Connexion utilisateur
 * @param {Object} credentials - Doit contenir { pseudo, password }
 */
export async function login(credentials) {
  // Envoie : { login "pseudo", password: "..." }
  const res = await API.post("/api/auth/login", credentials);

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
