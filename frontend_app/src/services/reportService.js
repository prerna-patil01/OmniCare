import api from "./api";
export default {
  async list() { return (await api.get("/api/reports")).data.data; },
  async upload(file) {
    const form = new FormData();
    form.append("file", file);
    return (await api.post("/api/reports/upload", form, { headers: { "Content-Type": "multipart/form-data" } })).data.data;
  },
};
