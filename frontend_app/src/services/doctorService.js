import api from "./api";

/* ==========================================================
   OmniCare Doctor Service
   ========================================================== */

const doctorService = {
  /* ----------------------------------------------------------
     Get All Doctors
  ---------------------------------------------------------- */
  async getDoctors(filters = {}) {
    try {
      const params = {};

      if (filters.specialty)
        params.specialty = filters.specialty;

      if (filters.maxFee)
        params.max_fee = filters.maxFee;

      if (filters.video)
        params.video = true;

      if (filters.sort)
        params.sort = filters.sort;

      const response = await api.get("/api/doctors", {
        params,
      });

      return response.data.data;
    } catch (error) {
      console.error("Unable to fetch doctors:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Search Doctors
  ---------------------------------------------------------- */
  async searchDoctors(query) {
    try {
      const response = await api.get(
        "/api/doctors/search",
        {
          params: {
            q: query,
          },
        }
      );

      return response.data.data;
    } catch (error) {
      console.error("Doctor search failed:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Doctor Details
  ---------------------------------------------------------- */
  async getDoctor(id) {
    try {
      const response = await api.get(
        `/api/doctors/${id}`
      );

      return response.data.data;
    } catch (error) {
      console.error("Unable to fetch doctor:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Doctors by Specialty
  ---------------------------------------------------------- */
  async getBySpecialty(specialty) {
    return await this.getDoctors({
      specialty,
    });
  },

  /* ----------------------------------------------------------
     Video Consultation Doctors
  ---------------------------------------------------------- */
  async getVideoDoctors() {
    return await this.getDoctors({
      video: true,
    });
  },

  /* ----------------------------------------------------------
     Affordable Doctors
  ---------------------------------------------------------- */
  async getAffordableDoctors(maxFee = 1000) {
    return await this.getDoctors({
      maxFee,
      sort: "fee",
    });
  },

  /* ----------------------------------------------------------
     Top Rated Doctors
  ---------------------------------------------------------- */
  async getTopRatedDoctors() {
    return await this.getDoctors({
      sort: "rating",
    });
  },

  /* ----------------------------------------------------------
     Nearby Doctors
  ---------------------------------------------------------- */
  async getNearbyDoctors() {
    return await this.getDoctors({
      sort: "distance",
    });
  },

  /* ----------------------------------------------------------
     Most Experienced Doctors
  ---------------------------------------------------------- */
  async getExperiencedDoctors() {
    return await this.getDoctors({
      sort: "experience",
    });
  },
};

export default doctorService;