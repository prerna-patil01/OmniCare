import axios from "axios";

/* ============================================================
   OmniCare API Client
   ============================================================ */

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

/* ============================================================
   Request Interceptor
   Automatically attach JWT token
   ============================================================ */

api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem("token") ||
      sessionStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

/* ============================================================
   Response Interceptor
   ============================================================ */

api.interceptors.response.use(
  (response) => response,

  (error) => {
    console.error("API Error:", error);

    if (error.response) {
      switch (error.response.status) {
        case 400:
          console.warn("Bad Request");
          break;

        case 401:
          console.warn("Unauthorized");

          localStorage.removeItem("token");
          sessionStorage.removeItem("token");

          break;

        case 403:
          console.warn("Forbidden");
          break;

        case 404:
          console.warn("Endpoint Not Found");
          break;

        case 500:
          console.warn("Internal Server Error");
          break;

        default:
          console.warn(error.response.data);
      }
    } else if (error.request) {
      console.error("Backend server is not running.");
    }

    return Promise.reject(error);
  }
);

/* ============================================================
   Health Check
   ============================================================ */

export async function pingServer() {
  try {
    const res = await api.get("/");

    return {
      online: true,
      data: res.data,
    };
  } catch {
    return {
      online: false,
    };
  }
}

export default api;