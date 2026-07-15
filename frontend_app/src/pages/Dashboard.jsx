import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  HeartPulse, Activity, Wind, Moon, UploadCloud, Sparkles,
  Pill, Car, HeartHandshake, ArrowRight, Check, Radar, CalendarDays,
} from "lucide-react";
import { cascade, riseIn, EASE } from "../lib/motion";
import { cn } from "../lib/cn";
import { DEMO_USER } from "../data/user";
import { VITALS, FULFILLMENT } from "../data/dashboard";
import { openUber } from "../lib/rides";

/* ─────────────────────────────────────────────────────────────
   THE BRIEFING

   White page. Black hero. Brown accent. Three values, nothing else.

   The hero is genuinely black — the strongest contrast available on
   white, and the reason the page has a focal point at all. Brown is
   the AI voice; it appears only where Omni speaks.
   ───────────────────────────────────────────────────────────── */

/* ═══ THE FINDING ══════════════════════════════════════════════ */

function Finding() {
  const navigate = useNavigate();

  const trail = [
    "Pain in your upper right side since Sunday",
    "Worse after fatty food",
    "Radiates to the right shoulder",
    "No fever, no jaundice",
  ];

  return (
    <motion.section
      variants={riseIn}
      className="grain relative overflow-hidden rounded-card"
      style={{ background: "var(--oc-hero)", color: "var(--oc-hero-fg)" }}
    >
      <motion.div
        animate={{ opacity: [0.25, 0.45, 0.25], scale: [1, 1.1, 1] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        className="pointer-events-none absolute -left-24 -top-28 h-80 w-80 rounded-full bg-brown-600/30 blur-[100px]"
      />

      <div className="relative grid lg:grid-cols-[1.3fr_1fr]">
        {/* Left — the conclusion */}
        <div className="p-9 lg:p-11">
          <div className="mb-6 flex items-center gap-2.5 text-brown-300">
            <Sparkles size={13} strokeWidth={2.2} />
            <p className="type-label">Omni · Clinical Finding</p>
          </div>

          <h2 className="type-hero max-w-[440px]">
            This looks like your <em className="serif">gallbladder</em>.
          </h2>

          <p className="mt-5 max-w-[430px] text-[17px] leading-relaxed opacity-70">
            Most likely biliary colic — gallstones irritating the duct. Not an
            emergency, but it needs a doctor within 48 hours.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <button
              onClick={() => navigate("/doctors")}
              className="group inline-flex h-12 items-center gap-2.5 rounded-full bg-brown-500 px-6 text-[15px] font-bold text-ink-950 transition-transform hover:scale-[1.02]"
            >
              Book a doctor
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
            </button>
            <button
              onClick={() => navigate("/omni")}
              className="inline-flex h-12 items-center rounded-full border border-white/25 px-6 text-[15px] font-bold transition-colors hover:bg-white/10"
            >
              Ask Omni more
            </button>
          </div>
        </div>

        {/* Right — the receipt */}
        <div className="border-t border-white/12 p-9 lg:border-l lg:border-t-0 lg:p-10">
          <div className="mb-6 flex items-center justify-between">
            <p className="type-label opacity-55">How Omni got here</p>
            <span className="rounded-full border border-white/20 px-2.5 py-1 text-[12px] font-bold opacity-70">
              4 turns
            </span>
          </div>

          <ul className="relative space-y-4 pl-5">
            <span className="absolute left-[3px] top-2 h-[calc(100%-16px)] w-px bg-white/20" />
            {trail.map((t, i) => (
              <motion.li
                key={t}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.1, duration: 0.45, ease: EASE }}
                className="relative text-[15px] leading-snug opacity-80"
              >
                <span className="absolute -left-5 top-[7px] h-[7px] w-[7px] rounded-full bg-brown-300" />
                {t}
              </motion.li>
            ))}
          </ul>

          <div className="mt-8 border-t border-white/12 pt-6">
            <div className="mb-3 flex items-baseline justify-between">
              <p className="type-label opacity-55">Risk</p>
              <p className="text-[15px] font-bold text-brown-300">Medium</p>
            </div>
            <div className="flex items-end gap-4">
              <p className="type-numeral">
                6.4<span className="ml-1 text-[15px] font-normal opacity-50">/ 10</span>
              </p>
              <div className="mb-1.5 h-1.5 flex-1 overflow-hidden rounded-full bg-white/15">
                <motion.div
                  className="h-full rounded-full bg-brown-400"
                  initial={{ width: 0 }}
                  animate={{ width: "64%" }}
                  transition={{ duration: 1.2, ease: EASE, delay: 0.5 }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.section>
  );
}

/* ═══ VITALS ═══════════════════════════════════════════════════ */

const VITAL_ICONS = { hr: HeartPulse, hrv: Activity, spo2: Wind, sleep: Moon };

function Vitals() {
  return (
    <motion.section variants={riseIn} className="border-y border-line py-6">
      <div className="mb-5 flex items-center gap-2">
        <motion.span
          className="h-1.5 w-1.5 rounded-full bg-vital-green"
          animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
        <p className="type-label text-fg-muted">Live from your watch</p>
      </div>

      <div className="grid grid-cols-4 gap-8">
        {VITALS.map((v) => {
          const Icon = VITAL_ICONS[v.key];
          return (
            <div key={v.key} className="flex items-baseline gap-3">
              <Icon size={15} strokeWidth={1.9} className="shrink-0 translate-y-0.5 text-fg-muted" />
              <div className="min-w-0">
                <p className="type-numeral-sm text-fg">
                  {v.value}
                  <span className="ml-1 text-[13px] font-normal text-fg-muted">{v.unit}</span>
                </p>
                <p className="mt-1 truncate text-[13px] text-fg-muted">{v.label}</p>
              </div>
            </div>
          );
        })}
      </div>
    </motion.section>
  );
}

/* ═══ IN MOTION ════════════════════════════════════════════════ */

function InMotion() {
  const navigate = useNavigate();
  const { transit, care } = FULFILLMENT;

  const rows = [
    { icon: Pill, label: "Medicines routed", detail: "Pantoprazole · ORS — 7:40 PM", to: "/pharmacy" },
    { icon: Car, label: "Ride booked", detail: `Uber — ${transit.eta} to Apollo`, action: () => openUber(transit), cta: "Open" },
    { icon: HeartHandshake, label: "Nurse on standby", detail: `${care[0].name} — ${care[0].rate}`, to: "/care" },
    { icon: CalendarDays, label: "Slots held", detail: "3 doctors free tomorrow morning", to: "/appointments" },
  ];

  return (
    <motion.section variants={riseIn} className="paper p-7">
      <div className="mb-5 flex items-center gap-2 text-vital-green">
        <Check size={13} strokeWidth={2.6} />
        <p className="type-label">Omni already handled this</p>
      </div>

      {rows.map((r) => (
        <motion.button
          key={r.label}
          whileHover={{ x: 3 }}
          transition={{ duration: 0.25, ease: EASE }}
          onClick={r.action ?? (() => navigate(r.to))}
          className="group flex w-full items-center gap-3.5 border-t border-line py-3.5 text-left first:border-0 first:pt-0"
        >
          <r.icon size={16} strokeWidth={1.9} className="shrink-0 text-vital-green" />
          <div className="min-w-0 flex-1">
            <p className="text-[16px] font-bold leading-tight text-fg">{r.label}</p>
            <p className="mt-0.5 truncate text-[13px] text-fg-muted">{r.detail}</p>
          </div>
          <span className="shrink-0 text-[13px] font-bold text-accent opacity-0 transition-opacity group-hover:opacity-100">
            {r.cta ?? "View"} →
          </span>
        </motion.button>
      ))}
    </motion.section>
  );
}

/* ═══ LOCAL SIGNAL ═════════════════════════════════════════════ */

function LocalSignal() {
  const navigate = useNavigate();

  const signals = [
    { label: "Viral fever", value: "↑ 4.2%", note: "Above seasonal baseline", tone: "amber" },
    { label: "Air quality", value: "AQI 118", note: "Moderate — sensitive groups", tone: "amber" },
    { label: "Dengue", value: "12 cases", note: "Reported nearby this week", tone: "red" },
    { label: "Flu shots", value: "Available", note: "3 clinics within 4 km", tone: "green" },
  ];

  const tones = { amber: "text-vital-amber", red: "text-vital-red", green: "text-vital-green" };

  return (
    <motion.section
      variants={riseIn}
      onClick={() => navigate("/intelligence")}
      className="paper cursor-pointer p-7"
    >
      <div className="mb-5 flex items-center justify-between">
        <div className="flex items-center gap-2 text-fg-muted">
          <Radar size={13} strokeWidth={2.2} />
          <p className="type-label">In Artist Village right now</p>
        </div>
        <span className="text-[12px] font-bold text-fg-muted">Last 7 days</span>
      </div>

      {signals.map((s) => (
        <div key={s.label} className="flex items-center gap-3.5 border-t border-line py-3.5 first:border-0 first:pt-0">
          <div className="min-w-0 flex-1">
            <p className="text-[16px] font-bold leading-tight text-fg">{s.label}</p>
            <p className="mt-0.5 truncate text-[13px] text-fg-muted">{s.note}</p>
          </div>
          <p className={cn("tabular shrink-0 text-[16px] font-bold", tones[s.tone])}>{s.value}</p>
        </div>
      ))}
    </motion.section>
  );
}

/* ═══ INGESTION ════════════════════════════════════════════════ */

function Ingestion() {
  const [dragging, setDragging] = useState(false);

  return (
    <motion.button
      variants={riseIn}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); }}
      whileHover={{ y: -3, transition: { duration: 0.3, ease: EASE } }}
      className={cn(
        "flex items-center gap-3.5 rounded-full border-2 border-dashed px-5 py-3 text-left transition-all duration-300",
        dragging
          ? "border-accent bg-brand-soft shadow-gold"
          : "border-accent/45 hover:border-accent hover:bg-brand-soft hover:shadow-gold"
      )}
    >
      <motion.span
        animate={{ y: dragging ? -3 : 0 }}
        className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-brand-soft text-accent"
      >
        <UploadCloud size={17} strokeWidth={1.9} />
      </motion.span>
      <div className="min-w-0">
        <p className="text-[15px] font-bold leading-tight text-fg">Drop a report</p>
        <p className="text-[12.5px] text-fg-muted">Labs · Rx · MRI · CT</p>
      </div>
    </motion.button>
  );
}

/* ═══ PAGE ═════════════════════════════════════════════════════ */

export default function Dashboard() {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  return (
    <motion.div
      variants={cascade(0.08)}
      initial="initial"
      animate="animate"
      className="mx-auto max-w-[1180px]"
    >
      <motion.header
        variants={riseIn}
        className="mb-7 flex flex-wrap items-center justify-between gap-5"
      >
        <div>
          <p className="type-eyebrow mb-2.5 text-fg-muted">{today}</p>
          <h1 className="text-[32px] font-bold leading-none tracking-[-0.02em] text-fg">
            Good to see you, <em className="serif">{DEMO_USER.name.split(" ")[0]}</em>.
          </h1>
        </div>
        <Ingestion />
      </motion.header>

      <div className="grid gap-6">
        <Finding />
        <Vitals />
        <div className="grid gap-6 lg:grid-cols-2">
          <InMotion />
          <LocalSignal />
        </div>
      </div>
    </motion.div>
  );
}