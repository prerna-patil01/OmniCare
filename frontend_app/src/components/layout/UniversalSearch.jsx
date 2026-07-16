import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Search, Command } from "lucide-react";
import { cn } from "../../lib/cn";
import doctorService from "../../services/doctorService";
import pharmacyService from "../../services/pharmacyService";

export default function UniversalSearch({ className }) {
  const [focused, setFocused] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const navigate = useNavigate();
  const search = async (value) => {
    setQuery(value);
    if (value.trim().length < 2) return setResults([]);
    const [doctors, medicines] = await Promise.allSettled([doctorService.searchDoctors(value), pharmacyService.search(value)]);
    setResults([
      ...(doctors.status === "fulfilled" ? doctors.value.map(x => ({ ...x, to: "/doctors", kind: "Doctor" })) : []),
      ...(medicines.status === "fulfilled" ? medicines.value.map(x => ({ ...x, to: "/pharmacy", kind: "Medicine" })) : []),
    ].slice(0, 6));
  };

  return (
    <motion.div
      animate={{ scale: focused ? 1.01 : 1 }}
      transition={{ duration: 0.25 }}
      className={cn(
        "flex h-11 items-center gap-3 rounded-full border bg-card px-4 transition-all duration-250",
        focused
          ? "border-azure-500/70 ring-4 ring-azure-500/12"
          : "border-line hover:border-line-strong",
        className
      )}
    >
      <Search size={16} strokeWidth={2} className="shrink-0 text-fg-muted" />
      <input
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        value={query}
        onChange={(e) => search(e.target.value)}
        placeholder="Search doctors, records, medicines, symptoms…"
        className="w-full bg-transparent text-[14px] text-fg outline-none placeholder:text-fg-muted/75"
      />
      <span className="hidden shrink-0 items-center gap-0.5 rounded-md border border-line px-1.5 py-0.5 text-[10.5px] font-medium text-fg-muted md:flex">
        <Command size={10} /> K
      </span>
      {results.length > 0 && <div className="absolute top-12 z-50 w-full overflow-hidden rounded-xl border border-line bg-card shadow-lift">{results.map(item => <button key={`${item.kind}-${item.id}`} onMouseDown={() => navigate(item.to)} className="block w-full px-4 py-3 text-left hover:bg-surface"><b>{item.name}</b><small className="ml-2 text-fg-muted">{item.kind}</small></button>)}</div>}
    </motion.div>
  );
}
