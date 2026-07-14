import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import {
  Stethoscope, HeartHandshake, CalendarDays, FolderHeart, FlaskConical,
  Pill, Sparkles, Activity, Radar, ShieldCheck, Siren, Car,
} from "lucide-react";

import AppLayout from "./components/layout/AppLayout";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Placeholder from "./pages/Placeholder";

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

          <Route path="/doctors" element={<Placeholder icon={Stethoscope} title="Find Doctors" description="Search by specialisation, symptom, distance, fee and rating. Video, in-clinic and second opinions in one flow." />} />
          <Route path="/care" element={<Placeholder icon={HeartHandshake} title="Care Services" description="Nurses, caretakers, ASHA and ANM workers, physiotherapists, dieticians and home sample collection — booked by the hour." />} />
          <Route path="/appointments" element={<Placeholder icon={CalendarDays} title="Appointments" description="Every consultation — online, video and in-person — on one calendar." />} />
          <Route path="/rides" element={<Placeholder icon={Car} title="Rides" description="Uber, Ola and Google Maps — destination pre-filled from your appointment, ETA tracked against your slot." />} />
          <Route path="/records" element={<Placeholder icon={FolderHeart} title="Health Records" description="A single timeline for reports, prescriptions, scans, notes and vaccinations. Categorised automatically." />} />
          <Route path="/reports" element={<Placeholder icon={FlaskConical} title="Reports & Labs" description="Upload a report and Omni extracts biomarkers, flags abnormal values and explains what they mean." />} />
          <Route path="/pharmacy" element={<Placeholder icon={Pill} title="Pharmacy" description="Prescription upload, price comparison, availability and delivery — connected to your records." />} />
          <Route path="/omni" element={<Placeholder icon={Sparkles} title="Ask Omni" description="A clinical copilot that probes deeper instead of guessing. Text, voice, images and PDFs." />} />
          <Route path="/insights" element={<Placeholder icon={Activity} title="Health Insights" description="Sleep, stress, hydration, activity, nutrition and heart health — trended weekly and monthly." />} />
          <Route path="/intelligence" element={<Placeholder icon={Radar} title="Disease Intelligence" description="Regional outbreak trends, air quality, seasonal risk and public health alerts near you." />} />
          <Route path="/insurance" element={<Placeholder icon={ShieldCheck} title="Insurance" description="Policies, coverage, cashless network and claim tracking in one place." />} />
          <Route path="/sos" element={<Placeholder icon={Siren} title="Emergency SOS" description="One tap reaches your hospital, ambulance, primary doctor and emergency contacts with your live location and medical summary." />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AnimatePresence>
  );
}