import api from "./api";

/* ==========================================================
   OmniCare Ride Service
   ========================================================== */

const rideService = {
  /* ----------------------------------------------------------
     Request Ride
  ---------------------------------------------------------- */
  async requestRide({
    lat,
    lng,
    destination,
    provider = "uber",
    urgency = "scheduled",
    triage_id = null,
  }) {
    try {
      const response = await api.post("/api/rides/request", {
        lat,
        lng,
        destination,
        provider,
        urgency,
        triage_id,
      });

      return response.data.data;
    } catch (error) {
      console.error("Unable to request ride:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     ETA
  ---------------------------------------------------------- */
  async getETA({
    from_lat,
    from_lng,
    to_lat,
    to_lng,
  }) {
    try {
      const response = await api.get("/api/rides/eta", {
        params: {
          from_lat,
          from_lng,
          to_lat,
          to_lng,
        },
      });

      return response.data.data;
    } catch (error) {
      console.error("Unable to fetch ETA:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Open Uber
  ---------------------------------------------------------- */
  openUber(ride) {
    if (ride?.links?.uber?.app) {
      window.open(ride.links.uber.app, "_blank");
    }
  },

  /* ----------------------------------------------------------
     Open Ola
  ---------------------------------------------------------- */
  openOla(ride) {
    if (ride?.links?.ola?.app) {
      window.open(ride.links.ola.app, "_blank");
    }
  },
};

export default rideService;