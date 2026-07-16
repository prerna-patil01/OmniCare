import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";

import AppLayout from "./components/layout/AppLayout";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/profile";
import Operations from "./pages/Operations";
import { Omni, SOS, Vitals } from "./pages/Clinical";

export default function App() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />

          <Route path="/doctors" element={<Operations type="doctors" />} />
          <Route path="/care" element={<Operations type="care" />} />
          <Route path="/appointments" element={<Operations type="appointments" />} />
          <Route path="/rides" element={<Operations type="rides" />} />
          <Route path="/records" element={<Operations type="records" />} />
          <Route path="/reports" element={<Operations type="reports" />} />
          <Route path="/pharmacy" element={<Operations type="pharmacy" />} />
          <Route path="/omni" element={<Omni />} />
          <Route path="/insights" element={<Vitals />} />
          <Route path="/intelligence" element={<Operations type="intelligence" />} />
          <Route path="/twin" element={<Operations type="twin" />} />
          <Route path="/insurance" element={<Operations type="insurance" />} />
          <Route path="/sos" element={<SOS />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AnimatePresence>
  );
}
