import api from "./api";

/* ==========================================================
   OmniCare Dashboard Service
   ========================================================== */

const dashboardService = {
  /**
   * Load every section needed for the Dashboard.
   */
  async loadDashboard() {
    try {
      const [profileRes, vitalsRes, intelligenceRes] =
        await Promise.allSettled([
          api.get("/api/profile"),
          api.get("/api/vitals"),
          api.get("/api/intelligence/regional"),
        ]);

      return {
        profile:
          profileRes.status === "fulfilled"
            ? profileRes.value.data.data
            : null,

        vitals:
          vitalsRes.status === "fulfilled"
            ? vitalsRes.value.data.data
            : null,

        intelligence:
          intelligenceRes.status === "fulfilled"
            ? intelligenceRes.value.data.data
            : null,
      };
    } catch (error) {
      console.error("Dashboard Service Error:", error);
      throw error;
    }
  },

  async loadProfile() {
    const res = await api.get("/api/profile");
    return res.data.data;
  },

  async loadVitals() {
    const res = await api.get("/api/vitals");
    return res.data.data;
  },

  async loadRegionalSignals(region = "") {
    const endpoint = region
      ? `/api/intelligence/regional?region=${encodeURIComponent(region)}`
      : "/api/intelligence/regional";

    const res = await api.get(endpoint);

    return res.data.data;
  },
};

export default dashboardService;