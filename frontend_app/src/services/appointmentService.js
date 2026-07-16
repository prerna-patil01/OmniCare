import api from "./api";

/* ==========================================================
   OmniCare Appointment Service
   ========================================================== */

const appointmentService = {
  /* ----------------------------------------------------------
     Get User Appointments
  ---------------------------------------------------------- */
  async getAppointments() {
    try {
      const response = await api.get("/api/appointments");

      return response.data.data;
    } catch (error) {
      console.error("Unable to fetch appointments:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Book Appointment
  ---------------------------------------------------------- */
  async bookAppointment({
    doctor_id,
    slot,
    mode = "in_person",
    triage_id = null,
  }) {
    try {
      const response = await api.post(
        "/api/appointments/book",
        {
          doctor_id,
          slot,
          mode,
          triage_id,
        }
      );

      return response.data.data;
    } catch (error) {
      console.error("Booking failed:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Cancel Appointment
  ---------------------------------------------------------- */
  async cancelAppointment(id) {
    try {
      const response = await api.post(
        `/api/appointments/${id}/cancel`
      );

      return response.data.data;
    } catch (error) {
      console.error("Unable to cancel appointment:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Join Video Consultation
  ---------------------------------------------------------- */
  async getVideoRoom(id) {
    try {
      const response = await api.get(
        `/api/appointments/${id}/video`
      );

      return response.data.data;
    } catch (error) {
      console.error("Unable to create video room:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Voice Assistant
  ---------------------------------------------------------- */
  async getVoiceAssistant(id) {
    try {
      const response = await api.get(
        `/api/appointments/${id}/voice`
      );

      return response.data.data;
    } catch (error) {
      console.error("Unable to connect voice assistant:", error);
      throw error;
    }
  },

  /* ----------------------------------------------------------
     Upcoming Appointment
  ---------------------------------------------------------- */
  async getUpcomingAppointment() {
    const appointments = await this.getAppointments();

    if (!appointments || appointments.length === 0)
      return null;

    return appointments.find(
      (appointment) =>
        appointment.status === "confirmed"
    );
  },

  /* ----------------------------------------------------------
     Has Confirmed Appointment?
  ---------------------------------------------------------- */
  async hasConfirmedAppointment() {
    const appointments = await this.getAppointments();

    return appointments.some(
      (appointment) =>
        appointment.status === "confirmed"
    );
  },
};

export default appointmentService;