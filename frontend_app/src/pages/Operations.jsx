import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import doctorService from "../services/doctorService";
import appointmentService from "../services/appointmentService";
import careService from "../services/careService";
import pharmacyService from "../services/pharmacyService";
import reportService from "../services/reportService";
import twinService from "../services/twinService";
import intelligenceService from "../services/intelligenceService";
import omniService from "../services/omniService";
import rideService from "../services/rideService";

const config = {
  doctors: { title: "Find Doctors", load: () => doctorService.getDoctors() },
  appointments: { title: "Appointments", load: () => appointmentService.getAppointments() },
  care: { title: "Care Services", load: () => careService.workers().then(x => x.workers) },
  reports: { title: "Reports & Labs", load: () => reportService.list() },
  records: { title: "Health Records", load: () => Promise.all([reportService.list(), api.get("/api/profile")]).then(([reports, profile]) => ({ reports, profile: profile.data.data })) },
  pharmacy: { title: "Pharmacy", load: () => pharmacyService.orders() },
  intelligence: { title: "Disease Intelligence", load: () => intelligenceService.regional() },
  twin: { title: "Digital Twin", load: () => twinService.get() },
  rides: { title: "Ride Booking", load: () => Promise.resolve([]) },
  insurance: { title: "Insurance", load: () => api.get("/api/insurance").then(r => r.data.data) },
};

const pretty = (value) => value == null || value === "" ? "—" : typeof value === "object" ? JSON.stringify(value) : String(value);

export default function Operations({ type }) {
  const page = config[type]; const navigate = useNavigate();
  const [data, setData] = useState(null); const [error, setError] = useState(""); const [query, setQuery] = useState(""); const [busy, setBusy] = useState(false);
  const load = useCallback(async () => { try { setError(""); setData(await page.load()); } catch (e) { setError(e?.response?.data?.error || "Unable to load this information."); } }, [page]);
  useEffect(() => { load(); }, [load]);
  const action = async (item) => {
    setBusy(true); try {
      if (type === "doctors") { await appointmentService.bookAppointment({ doctor_id: item.id, slot: item.next_slot, mode: item.video_available ? "video" : "in_person" }); navigate("/appointments"); }
      else if (type === "care") { await careService.book({ worker_id: item.id, starts_at: item.available_from }); load(); }
      else if (type === "appointments" && item.status === "confirmed") { await appointmentService.cancelAppointment(item.id); load(); }
      else if (type === "reports") document.getElementById("report-file")?.click();
      else if (type === "twin") { setData(await twinService.recompute()); }
      else if (type === "rides") { const ride = await rideService.requestRide({ destination: "Nearest hospital", provider: "uber" }); window.open(ride.links?.uber?.app, "_blank", "noopener"); }
    } catch (e) { setError(e?.response?.data?.error || "That request could not be completed."); } finally { setBusy(false); }
  };
  const upload = async (e) => { const file = e.target.files?.[0]; if (!file) return; setBusy(true); try { await reportService.upload(file); load(); } catch (x) { setError(x?.response?.data?.error || "Upload failed."); } finally { setBusy(false); } };
  if (type === "pharmacy") return <Pharmacy/>;
  if (type === "intelligence") return <Intelligence data={data} error={error}/>;
  if (type === "records") return <Records data={data} error={error}/>;
  const list = Array.isArray(data) ? data : data ? [data] : [];
  const visible = list.filter(x => JSON.stringify(x).toLowerCase().includes(query.toLowerCase()));
  return <div className="mx-auto max-w-[1180px]"><div className="mb-7 flex flex-wrap items-center justify-between gap-4"><div><p className="type-eyebrow text-fg-muted">OmniCare</p><h1 className="mt-2 text-3xl font-bold">{page.title}</h1></div>{["doctors", "care"].includes(type) && <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search" className="rounded-full border border-line bg-card px-4 py-2"/>}</div>{error && <p className="mb-4 rounded-xl bg-vital-red/10 p-3 text-vital-red">{error}</p>}{type === "reports" && <input id="report-file" type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" className="hidden" onChange={upload}/>}<div className="grid gap-4">{visible.map((item, index) => <article key={item.id || index} className="paper p-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><h2 className="text-lg font-bold">{item.name || item.filename || item.title || item.destination || item.worker?.name || item.doctor?.name || page.title}</h2><p className="mt-1 text-fg-muted">{item.specialty || item.role || item.document_type || item.status || item.narrative || item.trajectory || "No records yet."}</p></div>{["doctors","care","appointments","reports","twin","rides"].includes(type) && <button disabled={busy} onClick={()=>action(item)} className="rounded-full bg-ink-900 px-4 py-2 text-sm font-bold text-white disabled:opacity-50">{type === "doctors" ? "Book" : type === "care" ? "Book care" : type === "appointments" ? "Cancel" : type === "reports" ? "Upload report" : type === "twin" ? "Recompute" : "Request ride"}</button>}</div><dl className="mt-4 grid gap-2 text-sm text-fg-muted sm:grid-cols-3">{Object.entries(item).filter(([k,v]) => !["id","name","filename","title","narrative"].includes(k) && typeof v !== "object").slice(0,6).map(([k,v])=><div key={k}><dt className="capitalize">{k.replaceAll("_", " ")}</dt><dd className="font-semibold text-fg">{pretty(v)}</dd></div>)}</dl></article>)}{data !== null && !visible.length && <p className="paper p-6 text-fg-muted">No data is available yet.</p>}</div></div>;
}

function Pharmacy() { const [q,setQ]=useState(""); const [items,setItems]=useState([]); const [orders,setOrders]=useState([]); const [error,setError]=useState(""); const search=async()=>{try{setItems(await pharmacyService.search(q));setOrders(await pharmacyService.orders());}catch(e){setError(e?.response?.data?.error||"Unable to reach pharmacy.");}}; useEffect(()=>{search();},[]); const order=async(item)=>{try{await pharmacyService.order({items:[item]});search();}catch(e){setError(e?.response?.data?.error||"Order failed.");}}; return <div className="mx-auto max-w-[1180px]"><h1 className="mb-5 text-3xl font-bold">Pharmacy</h1><div className="flex gap-2"><input value={q} onChange={e=>setQ(e.target.value)} className="rounded-full border border-line px-4 py-2" placeholder="Search medicines"/><button onClick={search} className="rounded-full bg-ink-900 px-4 py-2 font-bold text-white">Search</button></div>{error&&<p className="mt-4 text-vital-red">{error}</p>}<div className="mt-5 grid gap-4">{items.map(m=><article className="paper flex justify-between p-5" key={m.id}><div><b>{m.name}</b><p className="text-fg-muted">{m.strength} · ₹{m.price_inr} · {m.delivery_eta}</p></div><button onClick={()=>order(m)} disabled={!m.in_stock} className="rounded-full bg-ink-900 px-4 py-2 text-white">Order</button></article>)}</div><h2 className="mt-8 text-xl font-bold">Your orders</h2>{orders.map(o=><p className="mt-2 paper p-4" key={o.id}>{o.status} · ₹{o.total_inr} · {o.eta}</p>)}</div>; }
function Intelligence({data,error}) { const items=[...(data?.signals||[]),...(data?.ambient||[])]; return <div className="mx-auto max-w-[1180px]"><h1 className="text-3xl font-bold">Disease Intelligence</h1><p className="mt-2 text-fg-muted">{data?.region}</p>{error&&<p className="text-vital-red">{error}</p>}<div className="mt-6 grid gap-4">{items.map((x,i)=><div className="paper p-5" key={i}><b>{x.label}</b><p>{x.value}</p><small className="text-fg-muted">{x.note}</small></div>)}{data?.suppressed&&<p className="paper p-5 text-fg-muted">{data.suppression_note}</p>}</div></div>; }
function Records({data,error}) { return <div className="mx-auto max-w-[1180px]"><h1 className="text-3xl font-bold">Health Records</h1>{error&&<p className="text-vital-red">{error}</p>}<section className="paper mt-5 p-5"><h2 className="font-bold">Profile</h2><pre className="mt-3 overflow-auto text-xs text-fg-muted">{JSON.stringify(data?.profile, null, 2)}</pre></section><section className="mt-5"><h2 className="font-bold">Reports</h2>{(data?.reports||[]).map(r=><p className="paper mt-3 p-4" key={r.id}>{r.filename} · {r.document_type}</p>)}</section></div>; }
