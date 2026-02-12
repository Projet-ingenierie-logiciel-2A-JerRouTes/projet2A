import API from "./apiClient";

export async function getAllUsers() {
  const res = await API.get("/api/users/");
  return res.data; // Renvoie la liste [UserPublic, ...]
}

export async function me() {
  const res = await API.get("/api/users/me");
  return res.data; // typiquement { user: {...} }
}

export async function updateMe({ username, email }) {
  const res = await API.patch("/api/users/me", { username, email });
  return res.data;
}

export async function changePassword({ old_password, new_password }) {
  const res = await API.post("/api/users/me/change-password", {
    old_password,
    new_password,
  });
  return res.data;
}
