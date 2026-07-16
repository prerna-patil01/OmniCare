import api from "./api";

export async function getProfile() {
  const response = await api.get("/api/profile");

  return response.data.data;
}