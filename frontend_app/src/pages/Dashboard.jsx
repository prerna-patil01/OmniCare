import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Activity, CalendarDays, HeartPulse, Radar, UploadCloud, Wind } from "lucide-react";
import dashboardService from "../services/dashboardService";
import omniService from "../services/omniService";
import reportService from "../services/reportService";

const vitalRows = [
  ["heart_rate", "Heart rate", "bpm", HeartPulse],
  ["hrv", "Heart-rate variability", "ms", Activity],
  ["spo2", "Blood oxygen", "%", Wind],
  ["sleep_hours", "Sleep", "hrs", CalendarDays],
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [finding, setFinding] = useState(null);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const load = async () => {
    try {
      const [dashboard, latestFinding] = await Promise.all([dashboardService.loadDashboard(), omniService.getLatestFinding()]);
      setData(dashboard); setFinding(latestFinding);
    } catch (e) { setError(e?.response?.data?.error || "Unable to load your health dashboard."); }
  };
  useEffect(() => { load(); }, []);
  const upload = async (event) => {
    const file = event.target.files?.[0]; if (!file) return;
    setUploading(true);
    try { await reportService.upload(file); navigate("/reports"); }
    catch (e) { setError(e?.response?.data?.error || "Report upload failed."); }
    finally { setUploading(false); }
  };
  const profile = data?.profile?.user;
  const vitals = data?.vitals?.latest;
  const regional = [...(data?.intelligence?.signals || []), ...(data?.intelligence?.ambient || [])];
  return <div className="mx-auto max-w-[1180px] space-y-6">
    <header className="flex flex-wrap items-center justify-between gap-4"><div><p className="type-eyebrow text-fg-muted">{new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" })}</p><h1 className="mt-2 text-[32px] font-bold text-fg">Good to see you, <em className="serif">{profile?.name?.split(" ")[0] || "there"}</em>.</h1></div><label className="flex cursor-pointer items-center gap-3 rounded-full border-2 border-dashed border-accent/45 px-5 py-3 font-bold text-fg"><UploadCloud size={18}/>{uploading ? "Uploading…" : "Drop a report"}<input className="hidden" type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={upload}/></label></header>
    {error && <p className="rounded-xl bg-vital-red/10 p-4 text-vital-red">{error}</p>}
    <section className="grain rounded-card bg-ink-950 p-8 text-white"><p className="type-label text-brown-300">Omni · Clinical finding</p>{finding ? <><h2 className="mt-4 text-3xl font-bold">{finding.clinical_term || finding.condition || "Latest clinical review"}</h2><p className="mt-3 max-w-2xl text-white/75">{finding.conclusion}</p><div className="mt-5 flex gap-3"><button onClick={() => navigate("/doctors")} className="rounded-full bg-brown-500 px-5 py-2 font-bold text-ink-950">Find a doctor</button><button onClick={() => navigate("/omni")} className="rounded-full border border-white/30 px-5 py-2 font-bold">Ask Omni</button></div></> : <><h2 className="mt-4 text-3xl font-bold">Your clinical review starts with a conversation.</h2><button onClick={() => navigate("/omni")} className="mt-5 rounded-full bg-brown-500 px-5 py-2 font-bold text-ink-950">Ask Omni</button></>}</section>
    <section className="grid grid-cols-2 gap-5 border-y border-line py-6 lg:grid-cols-4">{vitalRows.map(([key,label,unit,Icon]) => <div key={key} className="flex gap-3"><Icon className="mt-1 text-fg-muted" size={17}/><div><p className="text-2xl font-bold">{vitals?.[key] ?? "—"}<span className="ml-1 text-sm font-normal text-fg-muted">{vitals?.[key] != null ? unit : ""}</span></p><p className="text-sm text-fg-muted">{label}</p></div></div>)}</section>
    <section className="grid gap-6 lg:grid-cols-2"><div className="paper p-7"><h2 className="flex items-center gap-2 font-bold"><Radar size={17}/> Disease intelligence</h2><p className="mt-1 text-sm text-fg-muted">{data?.intelligence?.region || "Your region"}</p><div className="mt-5 space-y-3">{regional.length ? regional.map((signal, i) => <div key={`${signal.label}-${i}`} className="flex justify-between border-t border-line pt-3"><span><b>{signal.label}</b><small className="block text-fg-muted">{signal.note}</small></span><b>{signal.value}</b></div>) : <p className="text-fg-muted">No regional signals are available yet.</p>}</div></div><div className="paper p-7"><h2 className="font-bold">Your health record</h2><p className="mt-2 text-fg-muted">Profile, telemetry and reports are private and available to Omni only with your consent.</p><button onClick={() => navigate("/profile")} className="mt-5 font-bold text-accent">Open profile →</button></div></section>
  </div>;
}
