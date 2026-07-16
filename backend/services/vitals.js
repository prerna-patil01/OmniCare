import api from "./api";

export async function getVitals() {
  const response = await api.get("/api/vitals");

  return response.data.data;
}