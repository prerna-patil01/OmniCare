import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  HeartPulse, Activity, Wind, Moon, UploadCloud, Sparkles, Pill, Car,
  HeartHandshake, Building2, Radar, Siren, ShieldCheck, ArrowRight, TriangleAlert,
} from "lucide-react";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import Progress from "../components/ui/Progress";
import { cascade, riseIn, EASE } from "../lib/motion";
import { cn } from "../lib/cn";
import { DEMO_USER } from "../data/user";
import { VITALS, HABITS, OMNI_THREAD, FULFILLMENT, ECOSYSTEM } from "../data/dashboard";

/* ─────────────────────────────────────────────────────────────
   THE GRID — 2×2, one screen, no scrolling to find a quadrant.
   The architecture is expressed by the layout, not by labels
   announcing itself. Internal naming stays out of the product.
   ───────────────────────────────────────────────────────────── */

function Panel({ children, className, title, subtitle, icon: Icon, action, tone = "neutral" }) {
  const tones = {
    neutral: "text-navy-700 bg-brand-soft",
    red: "text-vital-red bg-vital-red/10",
    teal: "text-vital-teal bg-vital-teal/10",
    green: "text-vital-green bg-vital-green/10",
    gold: "text-gold-600 bg-gold-500/10 dark:text-gold-400",
  };

  return (
    <motion.section
      variants={riseIn}
      whileHover={{ y: -2, transition: { duration: 0.28, ease: EASE } }}
      className={cn(
        "flex flex-col rounded-[20px] border border-line bg-card p-5 shadow-soft transition-shadow hover:shadow-lift",
        className
      )}
    >
      <header className="mb-4 flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className={cn("grid h-9 w-9 shrink-0 place-items-center rounded-[11px]", tones[tone])}>
            <Icon size={17} strokeWidth={1.9} />
          </span>
          <div>
            <h2 className="text-[19px] font-bold leading-tight text-fg">{title}</h2>
            {subtitle && <p className="mt-0.5 text-[13px] leading-snug text-fg-muted">{subtitle}</p>}
          </div>
        </div>
        {action}
      </header>
      {children}
    </motion.section>
  );
}

/** Shared sub-card shell — one rhythm across all four panels. */
function Tile({ children, className, label, icon: Icon, right }) {
  return (
    <div className={cn("rounded-[14px] border border-line bg-surface/50 p-3.5", className)}>
      {label && (
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {Icon && <Icon size={13} strokeWidth={2} className="text-fg-muted" />}
            <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-fg-muted">{label}</p>
          </div>
          {right}
        </div>
      )}
      {children}
    </div>
  );
}

/* ═══ BIOMETRIC CANVAS ═════════════════════════════════════════ */

const VITAL_ICONS = { hr: HeartPulse, hrv: Activity, spo2: Wind, sleep: Moon };

function BiometricCanvas() {
  const [dragging, setDragging] = useState(false);

  return (
    <Panel
      title="Biometric Canvas"
      subtitle="Live telemetry · habits · ingestion"
      icon={HeartPulse}
      tone="red"
      action={<Badge tone="green" dot>Live</Badge>}
    >
      <div className="grid grid-cols-4 gap-2">
        {VITALS.map((v) => {
          const Icon = VITAL_ICONS[v.key];
          return (
            <motion.div
              key={v.key}
              whileHover={{ y: -2 }}
              className="rounded-[12px] border border-line bg-surface/50 p-2.5"
            >
              <div className="mb-1.5 flex items-center justify-between">
                <Icon size={12} strokeWidth={2} className="text-fg-muted" />
                <span className="tabular text-[11px] font-bold text-fg-muted">{v.delta}</span>
              </div>
              <p className="mb-0.5 text-[10px] font-bold uppercase tracking-[0.1em] text-fg-muted">
                {v.label}
              </p>
              <p className="tabular text-[21px] font-bold leading-none text-fg">
                {v.value}
                <span className="ml-0.5 text-[11px] font-normal text-fg-muted">{v.unit}</span>
              </p>
            </motion.div>
          );
        })}
      </div>

      <div className="mt-2 grid grid-cols-3 gap-2">
        {HABITS.map((h) => (
          <div key={h.label} className="rounded-[12px] border border-line bg-card p-2.5">
            <div className="mb-1.5 flex items-center justify-between">
              <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-fg-muted">{h.label}</p>
              {h.flag && <TriangleAlert size={11} className="text-vital-amber" />}
            </div>
            <p className="tabular mb-2 text-[17px] font-bold leading-none text-fg">
              {h.value}
              <span className="ml-0.5 text-[11px] font-normal text-fg-muted">{h.unit}</span>
            </p>
            <Progress value={h.pct} tone={h.tone === "teal" ? "brand" : h.tone} />
          </div>
        ))}
      </div>

      <motion.button
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); }}
        whileHover={{ scale: 1.005 }}
        className={cn(
          "mt-auto flex items-center gap-3 rounded-[14px] border-2 border-dashed p-3.5 pt-3.5 text-left transition-all duration-300",
          dragging
            ? "border-gold-500 bg-gold-500/10 shadow-gold"
            : "border-gold-500/40 bg-gold-500/[0.04] hover:border-gold-500 hover:shadow-gold"
        )}
        style={{ marginTop: "0.5rem" }}
      >
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-[11px] bg-gold-500/15 text-gold-600 dark:text-gold-400">
          <UploadCloud size={17} strokeWidth={1.9} />
        </span>
        <div className="min-w-0">
          <p className="text-[14px] font-bold text-fg">Ingestion Zone</p>
          <p className="truncate text-[12px] text-fg-muted">
            Drop reports, prescriptions, MRI or CT — parsed on arrival.
          </p>
        </div>
      </motion.button>
    </Panel>
  );
}

/* ═══ CLINICAL ENGINE ══════════════════════════════════════════ */

function ClinicalEngine() {
  const navigate = useNavigate();

  return (
    <Panel
      title="Clinical Engine"
      subtitle="Multi-turn probing, not flat Q&A"
      icon={Sparkles}
      tone="gold"
      action={<Badge tone="amber" dot>6.4 / 10</Badge>}
    >
      <div className="mb-3 rounded-[14px] border border-vital-amber/35 bg-vital-amber/8 p-3.5">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-vital-amber">
            System Triage
          </p>
          <span className="text-[12px] font-bold text-vital-amber">Medium</span>
        </div>
        <Progress value={64} tone="amber" />
        <p className="mt-2.5 text-[13px] leading-snug text-fg-soft">
          Consistent with biliary colic. Gastroenterologist within 48h.
        </p>
      </div>

      <div className="no-scrollbar max-h-[170px] flex-1 space-y-2 overflow-y-auto">
        {OMNI_THREAD.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.1, duration: 0.4, ease: EASE }}
            className={cn(
              "max-w-[93%] rounded-[13px] px-3 py-2 text-[13px] leading-snug",
              m.from === "omni"
                ? "border border-line bg-surface/60 text-fg-soft"
                : "ml-auto bg-brand-soft font-bold text-navy-700"
            )}
          >
            {m.text}
          </motion.div>
        ))}

        <div className="flex w-fit gap-1 rounded-[13px] border border-line bg-surface/60 px-3 py-2.5">
          {[0, 1, 2].map((i) => (
            <motion.span
              key={i}
              className="h-1 w-1 rounded-full bg-fg-muted"
              animate={{ opacity: [0.25, 1, 0.25] }}
              transition={{ duration: 1.1, repeat: Infinity, delay: i * 0.18 }}
            />
          ))}
        </div>
      </div>

      <Button size="sm" fullWidth className="mt-3" iconRight={ArrowRight} onClick={() => navigate("/omni")}>
        Continue with Omni
      </Button>
    </Panel>
  );
}

/* ═══ FULFILMENT MATRIX ════════════════════════════════════════ */

function StatusPill({ children }) {
  return (
    <span className="rounded bg-vital-green/12 px-1.5 py-0.5 text-[10px] font-bold tracking-[0.08em] text-vital-green">
      {children}
    </span>
  );
}

function FulfillmentMatrix() {
  const { pharmacy, transit, care } = FULFILLMENT;

  return (
    <Panel
      title="Fulfilment Matrix"
      subtitle="Pharmacy · transit · on-demand care"
      icon={Pill}
      tone="teal"
    >
      <div className="grid flex-1 gap-2">
        <Tile label="Pharmacy Pipeline" icon={Pill}>
          {pharmacy.map((m) => (
            <div key={m.name} className="flex items-center gap-2 border-t border-line py-2 first:border-0 first:pt-0">
              <div className="min-w-0 flex-1">
                <p className="truncate text-[14px] font-bold text-fg">{m.name}</p>
                <p className="text-[11px] text-fg-muted">{m.qty} · {m.eta}</p>
              </div>
              <StatusPill>{m.status}</StatusPill>
            </div>
          ))}
        </Tile>

        <Tile label="Transit · Uber / Ola" icon={Car} right={<StatusPill>{transit.status}</StatusPill>}>
          <div className="flex items-end justify-between">
            <div className="min-w-0">
              <p className="text-[14px] font-bold text-fg">{transit.provider}</p>
              <p className="truncate text-[11px] text-fg-muted">{transit.destination}</p>
            </div>
            <p className="tabular shrink-0 text-[21px] font-bold leading-none text-fg">
              {transit.eta.split(" ")[0]}
              <span className="ml-0.5 text-[11px] font-normal text-fg-muted">min</span>
            </p>
          </div>
        </Tile>

        <Tile label="On-Demand Care" icon={HeartHandshake}>
          {care.map((c) => (
            <div key={c.name} className="flex items-center gap-2 border-t border-line py-2 first:border-0 first:pt-0">
              <div className="min-w-0 flex-1">
                <p className="truncate text-[14px] font-bold text-fg">{c.name}</p>
                <p className="text-[11px] text-fg-muted">{c.role} · {c.rate}</p>
              </div>
              <Button size="sm" variant="secondary">{c.available}</Button>
            </div>
          ))}
        </Tile>
      </div>
    </Panel>
  );
}

/* ═══ ECOSYSTEM GRID ═══════════════════════════════════════════ */

function EcosystemGrid() {
  const navigate = useNavigate();
  const { hospital, epidemic } = ECOSYSTEM;

  return (
    <Panel
      title="Ecosystem Grid"
      subtitle="Hospitals · population · emergency"
      icon={Building2}
      tone="green"
    >
      <div className="grid flex-1 gap-2">
        <Tile
          label="Hospital Hub"
          icon={Building2}
          right={
            <span className="flex items-center gap-1 text-[11px] font-bold text-vital-green">
              <ShieldCheck size={11} /> Consent: {hospital.consent}
            </span>
          }
        >
          <div className="mb-2.5 flex items-baseline justify-between">
            <p className="text-[15px] font-bold text-fg">{hospital.name}</p>
            <p className="text-[12px] text-fg-muted">{hospital.distance}</p>
          </div>
          <div className="mb-1.5 flex items-center justify-between">
            <p className="text-[11px] font-bold text-fg-muted">ER load</p>
            <p className="tabular text-[12px] font-bold text-fg">{hospital.erLoad}%</p>
          </div>
          <Progress value={hospital.erLoad} tone="amber" />
        </Tile>

        <Tile label="Epidemic Tracker" icon={Radar} right={<Badge tone="amber" dot>{epidemic.trend}</Badge>}>
          <p className="tabular text-[21px] font-bold leading-none text-fg">
            {epidemic.index}
            <span className="ml-1 text-[11px] font-normal text-fg-muted">% viral index</span>
          </p>
          <p className="mt-1.5 text-[11px] text-fg-muted">
            {epidemic.region} · {epidemic.driver}
          </p>
        </Tile>

        <motion.button
          onClick={() => navigate("/sos")}
          whileHover={{ y: -2 }}
          whileTap={{ scale: 0.99 }}
          transition={{ duration: 0.25, ease: EASE }}
          className="mt-auto flex items-center gap-3 rounded-[14px] border border-vital-red/30 bg-vital-red/8 p-3.5 text-left transition-colors hover:bg-vital-red/12"
        >
          <span className="relative grid h-9 w-9 shrink-0 place-items-center rounded-[11px] bg-vital-red text-white">
            <motion.span
              className="absolute inset-0 rounded-[11px] bg-vital-red"
              animate={{ scale: [1, 1.35], opacity: [0.5, 0] }}
              transition={{ duration: 1.8, repeat: Infinity, ease: "easeOut" }}
            />
            <Siren size={17} strokeWidth={2} className="relative" />
          </span>
          <div className="min-w-0">
            <p className="text-[14px] font-bold text-vital-red">Critical SOS</p>
            <p className="truncate text-[12px] text-fg-soft">
              Location, blood group, allergies — one tap.
            </p>
          </div>
        </motion.button>
      </div>
    </Panel>
  );
}

/* ═══ PAGE ═════════════════════════════════════════════════════ */

export default function Dashboard() {
  return (
    <motion.div variants={cascade(0.06)} initial="initial" animate="animate">
      <motion.header variants={riseIn} className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.2em] text-fg-muted">
            {new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" })}
          </p>
          <h1 className="text-[40px] font-bold leading-none tracking-[-0.02em] text-fg">
            Good to see you, <em className="font-normal not-italic">{DEMO_USER.name.split(" ")[0]}</em>.
          </h1>
          <p className="mt-2.5 text-[15px] text-fg-soft">
            Three signals are drifting from baseline. Omni is already probing.
          </p>
        </div>
        <Badge tone="amber" dot>Attention advised</Badge>
      </motion.header>

      {/* 2×2 — all four visible without scrolling */}
      <div className="grid gap-4 lg:grid-cols-2">
        <BiometricCanvas />
        <ClinicalEngine />
        <FulfillmentMatrix />
        <EcosystemGrid />
      </div>
    </motion.div>
  );
}