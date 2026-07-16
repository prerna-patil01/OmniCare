import { useEffect, useState } from "react";
import profileService from "../services/profileService";

export default function Profile() {
  const [record, setRecord] = useState(null); const [error,setError]=useState(""); const [saving,setSaving]=useState(false);
  const load=async()=>{try{setRecord(await profileService.getProfile());}catch(e){setError(e?.response?.data?.error||"Unable to load your profile.");}};
  useEffect(()=>{load();},[]);
  const update=(section,key,value)=>setRecord(r=>({...r,[section]:{...(r[section]||{}),[key]:value}}));
  const save=async()=>{setSaving(true);try{await profileService.updateProfile({profile:record.profile,history:record.history,lifestyle:record.lifestyle});await load();}catch(e){setError(e?.response?.data?.error||"Unable to save profile.");}finally{setSaving(false);}};
  const fields=[...["gender","height_cm","weight_kg","blood_group","emergency_contact"].map(k=>["profile",k]),...["allergies","current_diseases","medications"].map(k=>["history",k]),...["smoking","alcohol","exercise","sleep","hydration_l","occupation"].map(k=>["lifestyle",k])];
  return <div className="mx-auto max-w-5xl"><header className="mb-7"><p className="type-eyebrow text-fg-muted">Health identity</p><h1 className="mt-2 text-3xl font-bold">{record?.user?.name||"My profile"}</h1><p className="mt-1 text-fg-muted">{record?.user?.email||record?.user?.phone||""}</p></header>{error&&<p className="mb-4 text-vital-red">{error}</p>}<section className="paper p-6"><div className="grid gap-5 sm:grid-cols-2">{fields.map(([section,key])=><label className="text-sm font-bold capitalize" key={`${section}-${key}`}>{key.replaceAll("_"," ")}<input value={Array.isArray(record?.[section]?.[key])?record[section][key].join(", "):(record?.[section]?.[key]??"")} onChange={e=>update(section,key,["allergies","current_diseases","medications"].includes(key)?e.target.value.split(",").map(x=>x.trim()).filter(Boolean):e.target.value)} className="mt-2 block w-full rounded-xl border border-line bg-card px-3 py-2 font-normal"/></label>)}</div><button disabled={saving||!record} onClick={save} className="mt-6 rounded-full bg-ink-900 px-5 py-2 font-bold text-white">{saving?"Saving…":"Save changes"}</button></section></div>;
}
