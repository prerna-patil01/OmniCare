import api from "./api";

export async function getSignals() {
  const response = await api.get("/api/intelligence");

  return response.data.data;
}