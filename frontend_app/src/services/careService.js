import api from "./api";

const careService = {
  async workers(params = {}) { return (await api.get("/api/care/workers", { params })).data.data; },
  async book(payload) { return (await api.post("/api/care/book", payload)).data.data; },
  async bookings() { return (await api.get("/api/care/bookings")).data.data; },
  async sampleCollection(payload) { return (await api.post("/api/care/sample-collection", payload)).data.data; },
};
export default careService;
