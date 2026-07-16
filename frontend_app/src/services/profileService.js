import api from "./api";

/* ==========================================================
   OmniCare Profile Service
   ========================================================== */

const profileService = {
  /* ----------------------------------------------------------
     Get User Profile
  ---------------------------------------------------------- */
  async getProfile() {
    try {
      const response = await api.get("/api/profile");

      return response.data.data;
    } catch (error) {
      console.error("Profile Fetch Failed:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Update Existing Profile
  ---------------------------------------------------------- */
  async updateProfile(profileData) {
    try {
      const response = await api.patch(
        "/api/profile",
        profileData
      );

      return response.data.data;
    } catch (error) {
      console.error("Profile Update Failed:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Complete Onboarding
  ---------------------------------------------------------- */
  async onboard(onboardingData) {
    try {
      const response = await api.post(
        "/api/profile/onboard",
        onboardingData
      );

      return response.data.data;
    } catch (error) {
      console.error("Onboarding Failed:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Refresh Profile
  ---------------------------------------------------------- */
  async refresh() {
    return await this.getProfile();
  },
};

export default profileService;