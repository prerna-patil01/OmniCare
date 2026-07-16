import api from "./api";
export default {
  async regional(region) { return (await api.get("/api/intelligence/regional", { params: region ? { region } : {} })).data.data; },
};
