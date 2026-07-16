import { useCallback, useEffect, useState } from "react";
import dashboardService from "../services/dashboardService";

export default function useDashboard() {
  const [dashboard, setDashboard] = useState({
    profile: null,
    vitals: null,
    intelligence: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await dashboardService.loadDashboard();

      setDashboard(data);
    } catch (err) {
      console.error("Dashboard Hook:", err);

      setError(
        err?.response?.data?.error ||
        err?.message ||
        "Unable to load dashboard."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  return {
    dashboard,
    loading,
    error,
    reload: loadDashboard,
  };
}