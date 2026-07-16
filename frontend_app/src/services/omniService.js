import api from "./api";

const omniService = {
  /* ---------------------------------------
     Chat with Omni
  --------------------------------------- */
  async chat(message, conversationId = null) {
    const response = await api.post("/api/omni/chat", {
      message,
      conversation_id: conversationId,
    });

    return response.data.data;
  },

  /* ---------------------------------------
     Previous Conversations
  --------------------------------------- */
  async getConversations() {
    const response = await api.get("/api/omni/conversations");
    return response.data.data;
  },

  /* ---------------------------------------
     Open Conversation
  --------------------------------------- */
  async getConversation(id) {
    const response = await api.get(`/api/omni/conversations/${id}`);
    return response.data.data;
  },

  /* ---------------------------------------
     Dashboard Finding
  --------------------------------------- */
  async getLatestFinding() {
    const response = await api.get("/api/omni/findings");
    return response.data.data;
  },

  /* ---------------------------------------
     Calibration
  --------------------------------------- */
  async getCalibration() {
    const response = await api.get("/api/omni/calibration");
    return response.data.data;
  },

  /* ---------------------------------------
     Human Signoff
  --------------------------------------- */
  async signoff(triageId, signer = "patient") {
    const response = await api.post(`/api/omni/signoff/${triageId}`, {
      signer,
    });

    return response.data.data;
  },

  /* ---------------------------------------
     Dispatch
  --------------------------------------- */
  async dispatch(triageId) {
    const response = await api.post(`/api/omni/dispatch/${triageId}`);

    return response.data.data;
  },

  /* ---------------------------------------
     Record Actual Outcome
  --------------------------------------- */
  async submitOutcome(
    triageId,
    actual_condition,
    correct = true,
    actual_severity = null,
    confirmed_by = "doctor"
  ) {
    const response = await api.post(`/api/omni/outcome/${triageId}`, {
      actual_condition,
      correct,
      actual_severity,
      confirmed_by,
    });

    return response.data.data;
  },
};

export default omniService;