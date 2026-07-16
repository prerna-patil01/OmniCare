import api from "./api";
export default {
  async get() { return (await api.get("/api/twin")).data.data; },
  async recompute() { return (await api.post("/api/twin/recompute")).data.data; },
  async history() { return (await api.get("/api/twin/history")).data.data; },
};
