import api from "./api";
export default {
  async search(q = "") { return (await api.get("/api/pharmacy/search", { params: { q } })).data.data; },
  async order(payload) { return (await api.post("/api/pharmacy/order", payload)).data.data; },
  async orders() { return (await api.get("/api/pharmacy/orders")).data.data; },
};
