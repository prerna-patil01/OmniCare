import api from "./api";

const authService = {
  async login(credentials) {
    const { data } = await api.post("/api/auth/login", credentials);
    return data.data;
  },
  async register(payload) {
    const { data } = await api.post("/api/auth/register", payload);
    return data.data;
  },
  async me() {
    const { data } = await api.get("/api/auth/me");
    return data.data.user;
  },
  storeSession(session, persistent = true) {
    const store = persistent ? localStorage : sessionStorage;
    store.setItem("token", session.token);
    store.setItem("user", JSON.stringify(session.user));
  },
  clearSession() {
    [localStorage, sessionStorage].forEach((store) => {
      store.removeItem("token");
      store.removeItem("user");
    });
  },
};

export default authService;
