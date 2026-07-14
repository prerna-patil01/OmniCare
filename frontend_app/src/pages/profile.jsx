import { useRef, useState } from "react";
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from "framer-motion";
import {
  Heart, Brain, Wind, Activity, Bone, Droplet, Hand, Scan, X, FileText,
  Clock, Stethoscope, TriangleAlert, Pill, FlaskConical, Ruler, Weight,
  ShieldCheck, Watch, IdCard, Eye, EyeOff,
} from "lucide-react";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import Progress from "../components/ui/Progress";
import { cascade, riseIn, EASE } from "../lib/motion";
import { cn } from "../lib/cn";
import { DEMO_USER } from "../data/user";

/* ─────────────────────────────────────────────────────────────
   ANATOMY EXPLORER
   Render asset: /public/assets/illustrations/anatomy-front.png
   (transparent PNG, front view). Placeholder shows until present.
   Hotspots are % of the stage — tune x/y to match your render.
   Parallax tilt + depth-layered markers give the 3D feel.
   ───────────────────────────────────────────────────────────── */

const SYSTEMS = [
  { id: "organs",      label: "Organs",      on: true },
  { id: "circulatory", label: "Circulatory", on: true },
  { id: "skeletal",    label: "Skeletal",    on: false },
  { id: "nervous",     label: "Nervous",     on: false },
];

const ORGANS = [
  {
    id: "brain", system: "nervous", name: "Brain", icon: Brain, x: 50, y: 6, risk: "low",
    summary: "No neurological findings. Migraine history noted in family line.",
    metrics: [{ label: "Migraine episodes", value: "2 / yr" }],
    reports: [], notes: "Family history: maternal migraine. Monitor frequency.",
    meds: [], tests: [],
  },
  {
    id: "heart", system: "organs", name: "Heart", icon: Heart, x: 47, y: 27, risk: "medium",
    summary: "Resting HR trending up over 14 days. HRV down 18%. Not yet clinically significant.",
    metrics: [{ label: "Resting HR", value: "72 bpm" }, { label: "HRV", value: "52 ms" }, { label: "BP", value: "118/76" }],
    reports: ["ECG — 12 Mar 2026", "Lipid Panel — 04 Jan 2026"],
    notes: "Dr. Menon: sinus rhythm normal. Repeat lipid panel in 6 months.",
    meds: [], tests: ["Lipid Panel — due Jul 2026"],
  },
  {
    id: "lungs", system: "organs", name: "Lungs", icon: Wind, x: 56, y: 25, risk: "low",
    summary: "SpO₂ stable at 98%. Non-smoker, no respiratory history.",
    metrics: [{ label: "SpO₂", value: "98%" }, { label: "Resp. rate", value: "14 /min" }],
    reports: ["Chest X-Ray — 22 Nov 2025"],
    notes: "Clear fields bilaterally.", meds: [], tests: [],
  },
  {
    id: "liver", system: "organs", name: "Liver", icon: Activity, x: 44, y: 38, risk: "high",
    summary: "ACTIVE FINDING — RUQ pain since Sunday, radiating to right scapula, worse post-prandially.",
    metrics: [{ label: "ALT", value: "48 U/L" }, { label: "AST", value: "41 U/L" }, { label: "Bilirubin", value: "1.3" }],
    reports: ["LFT Panel — 12 Jul 2026", "Ultrasound — PENDING"],
    notes: "Omni triage: pattern consistent with biliary colic. Gastroenterologist within 48h.",
    meds: ["Pantoprazole 40mg — ×14"], tests: ["Ultrasound Abdomen — 15 Jul"],
  },
  {
    id: "stomach", system: "organs", name: "Stomach", icon: Droplet, x: 54, y: 40, risk: "medium",
    summary: "Post-prandial discomfort — likely secondary to hepatobiliary complaint.",
    metrics: [{ label: "H. pylori", value: "Negative" }],
    reports: ["H. pylori Test — 12 Jul 2026"],
    notes: "Rule out gastritis after ultrasound.", meds: ["Pantoprazole 40mg"], tests: [],
  },
  {
    id: "kidneys", system: "organs", name: "Kidneys", icon: Scan, x: 50, y: 46, risk: "low",
    summary: "Renal function normal. Hydration chronically below baseline.",
    metrics: [{ label: "Creatinine", value: "0.8" }, { label: "eGFR", value: "> 90" }],
    reports: ["RFT — 04 Jan 2026"], notes: "Increase fluids to 3L/day.", meds: [], tests: [],
  },
  {
    id: "skin", system: "organs", name: "Skin", icon: Hand, x: 68, y: 54, risk: "low",
    summary: "Penicillin allergy presents as urticaria. No other findings.",
    metrics: [{ label: "Known allergy", value: "Penicillin" }],
    reports: [], notes: "Allergy flagged across prescribing surfaces.", meds: [], tests: [],
  },
  {
    id: "bones", system: "skeletal", name: "Bones", icon: Bone, x: 33, y: 62, risk: "low",
    summary: "No fractures. Vitamin D marginally low — correctable.",
    metrics: [{ label: "Vitamin D", value: "24 ng/mL" }],
    reports: ["Vitamin D Assay — 04 Jan 2026"],
    notes: "60,000 IU weekly × 8 weeks.", meds: [], tests: [],
  },
  {
    id: "joints", system: "skeletal", name: "Joints", icon: Activity, x: 66, y: 78, risk: "low",
    summary: "Occasional knee stiffness after prolonged sitting. Postural.",
    metrics: [{ label: "Mobility", value: "Full" }],
    reports: [], notes: "Movement breaks every 45 min.", meds: [], tests: [],
  },
];

const RISK_TONE = { low: "green", medium: "amber", high: "red" };
const RISK_HEX = {
  low: "var(--color-vital-green)",
  medium: "var(--color-vital-amber)",
  high: "var(--color-vital-red)",
};

/* ═══ HOTSPOT ══════════════════════════════════════════════════ */

function Hotspot({ organ, active, dimmed, onClick }) {
  const color = RISK_HEX[organ.risk];

  return (
    <motion.button
      onClick={onClick}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: dimmed ? 0.25 : 1, scale: 1 }}
      transition={{ delay: 0.4, duration: 0.4, ease: EASE }}
      whileHover={{ scale: 1.3 }}
      style={{ left: `${organ.x}%`, top: `${organ.y}%`, color, transform: "translateZ(46px)" }}
      className="group absolute z-20 -translate-x-1/2 -translate-y-1/2"
      aria-label={organ.name}
    >
      {organ.risk !== "low" && (
        <motion.span
          className="absolute inset-0 rounded-full"
          style={{ backgroundColor: color }}
          animate={{ scale: [1, 2.6], opacity: [0.5, 0] }}
          transition={{ duration: organ.risk === "high" ? 1.3 : 2, repeat: Infinity, ease: "easeOut" }}
        />
      )}
      <span
        className={cn(
          "relative grid h-[22px] w-[22px] place-items-center rounded-full border-2 border-card transition-all duration-250",
          active && "ring-4 ring-current/25"
        )}
        style={{ backgroundColor: color }}
      >
        <span className="h-1.5 w-1.5 rounded-full bg-white" />
      </span>
      <span className="pointer-events-none absolute left-1/2 top-full mt-2 -translate-x-1/2 whitespace-nowrap rounded-lg border border-line bg-card px-2.5 py-1 text-[13px] font-bold text-fg opacity-0 shadow-soft transition-opacity duration-200 group-hover:opacity-100">
        {organ.name}
      </span>
    </motion.button>
  );
}

/* ═══ ANOMALY LEADER CARD ══════════════════════════════════════ */

function AnomalyCallout({ organ, onOpen }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 1, duration: 0.6, ease: EASE }}
      style={{ left: `${organ.x + 14}%`, top: `${organ.y - 4}%` }}
      className="absolute z-30 hidden lg:block"
    >
      <svg width="60" height="30" className="absolute -left-[58px] top-5 overflow-visible">
        <motion.path
          d="M58 6 L20 6 L0 24"
          fill="none"
          stroke={RISK_HEX.high}
          strokeWidth="1.5"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ delay: 1.1, duration: 0.7, ease: EASE }}
        />
      </svg>
      <motion.button
        onClick={onOpen}
        whileHover={{ y: -3 }}
        className="w-[210px] rounded-[16px] border border-vital-red/35 bg-card p-4 text-left shadow-lift"
      >
        <p className="type-label mb-1.5 text-vital-red">Active Finding</p>
        <p className="text-[16px] font-bold leading-snug text-fg">{organ.name} — {organ.risk} risk</p>
        <p className="mt-1.5 text-[13px] leading-relaxed text-fg-muted">
          Biliary colic suspected · triage 6.4/10
        </p>
        <p className="mt-2.5 text-[13px] font-bold text-navy-700">View details →</p>
      </motion.button>
    </motion.div>
  );
}

/* ═══ SIDE PANEL ═══════════════════════════════════════════════ */

function OrganPanel({ organ, onClose }) {
  const Icon = organ.icon;

  const Section = ({ icon: I, title, children, empty }) => (
    <div className="border-t border-line py-5">
      <div className="mb-3 flex items-center gap-2.5">
        <I size={14} strokeWidth={2} className="text-fg-muted" />
        <p className="type-label text-fg-muted">{title}</p>
      </div>
      {empty ? <p className="text-[15px] italic text-fg-muted">{empty}</p> : children}
    </div>
  );

  return (
    <motion.aside
      initial={{ x: "100%", opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: "100%", opacity: 0 }}
      transition={{ duration: 0.45, ease: EASE }}
      className="absolute right-0 top-0 z-40 h-full w-full max-w-[420px] overflow-hidden rounded-card border border-line bg-card shadow-lift"
    >
      <div className="no-scrollbar h-full overflow-y-auto p-7">
        <div className="mb-5 flex items-start justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <span
              className="grid h-12 w-12 place-items-center rounded-[15px]"
              style={{
                backgroundColor: `color-mix(in srgb, ${RISK_HEX[organ.risk]} 12%, transparent)`,
                color: RISK_HEX[organ.risk],
              }}
            >
              <Icon size={22} strokeWidth={1.8} />
            </span>
            <div>
              <h3 className="type-cardtitle text-fg">{organ.name}</h3>
              <Badge tone={RISK_TONE[organ.risk]} dot className="mt-1.5">{organ.risk} risk</Badge>
            </div>
          </div>
          <button
            onClick={onClose}
            className="grid h-9 w-9 shrink-0 place-items-center rounded-full text-fg-muted transition-colors hover:bg-surface hover:text-fg"
            aria-label="Close"
          >
            <X size={17} />
          </button>
        </div>

        <p className="mb-5 text-[16px] leading-relaxed text-fg-soft">{organ.summary}</p>

        {organ.metrics.length > 0 && (
          <div className="grid grid-cols-2 gap-2.5">
            {organ.metrics.map((m) => (
              <div key={m.label} className="rounded-md2 border border-line bg-surface/60 p-3.5">
                <p className="type-label mb-1 text-fg-muted">{m.label}</p>
                <p className="tabular text-[19px] font-bold text-fg">{m.value}</p>
              </div>
            ))}
          </div>
        )}

        <Section icon={FileText} title="Reports" empty={organ.reports.length ? null : "No reports on file."}>
          <ul className="space-y-2">
            {organ.reports.map((r) => (
              <li key={r} className="flex items-center justify-between rounded-md2 border border-line px-3.5 py-2.5">
                <span className="text-[15px] text-fg-soft">{r}</span>
                <FileText size={14} className="text-fg-muted" />
              </li>
            ))}
          </ul>
        </Section>

        <Section icon={Stethoscope} title="Doctor Notes">
          <p className="rounded-md2 border-l-2 border-navy-700 bg-surface/50 px-4 py-3 text-[15px] italic leading-relaxed text-fg-soft">
            {organ.notes}
          </p>
        </Section>

        <Section icon={Pill} title="Medicines" empty={organ.meds.length ? null : "None prescribed."}>
          <ul className="space-y-2">
            {organ.meds.map((m) => (
              <li key={m} className="rounded-md2 bg-brand-soft px-3.5 py-2.5 text-[15px] font-bold text-navy-700">{m}</li>
            ))}
          </ul>
        </Section>

        <Section icon={FlaskConical} title="Tests" empty={organ.tests.length ? null : "None scheduled."}>
          <ul className="space-y-2">
            {organ.tests.map((t) => (
              <li key={t} className="rounded-md2 border border-line px-3.5 py-2.5 text-[15px] text-fg-soft">{t}</li>
            ))}
          </ul>
        </Section>

        <Section icon={Clock} title="Timeline">
          <div className="relative space-y-4 pl-5">
            <span className="absolute left-[3px] top-1.5 h-[calc(100%-12px)] w-px bg-line" />
            {[
              { d: "12 Jul 2026", e: "Symptom logged via Omni" },
              { d: "12 Jul 2026", e: "LFT panel ordered" },
              { d: "15 Jul 2026", e: "Ultrasound booked" },
            ].map((t, i) => (
              <div key={i} className="relative">
                <span className="absolute -left-5 top-2 h-[7px] w-[7px] rounded-full bg-navy-700 ring-2 ring-card" />
                <p className="text-[13px] font-bold text-fg-muted">{t.d}</p>
                <p className="text-[15px] text-fg-soft">{t.e}</p>
              </div>
            ))}
          </div>
        </Section>

        <Button size="lg" fullWidth className="mt-4">
          Consult about {organ.name.toLowerCase()}
        </Button>
      </div>
    </motion.aside>
  );
}

/* ═══ METRICS RAIL ═════════════════════════════════════════════ */

function MetricsRail() {
  const bmi = +(DEMO_USER.weightKg / (DEMO_USER.heightCm / 100) ** 2).toFixed(1);

  const stats = [
    { icon: Ruler, label: "Height", value: `${DEMO_USER.heightCm} cm` },
    { icon: Weight, label: "Weight", value: `${DEMO_USER.weightKg} kg` },
    { icon: Activity, label: "BMI", value: bmi, badge: { tone: "green", text: "Healthy" } },
    { icon: Droplet, label: "Blood group", value: DEMO_USER.bloodGroup },
  ];

  return (
    <motion.div variants={cascade(0.06)} initial="initial" animate="animate" className="grid gap-4">
      <motion.div variants={riseIn} className="grid grid-cols-2 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="rounded-lg2 border border-line bg-card p-4 shadow-soft">
            <div className="mb-2.5 flex items-center justify-between">
              <s.icon size={14} strokeWidth={2} className="text-fg-muted" />
              {s.badge && <Badge tone={s.badge.tone}>{s.badge.text}</Badge>}
            </div>
            <p className="type-label mb-1 text-fg-muted">{s.label}</p>
            <p className="tabular text-[22px] font-bold text-fg">{s.value}</p>
          </div>
        ))}
      </motion.div>

      <motion.div variants={riseIn} className="rounded-lg2 border border-vital-red/30 bg-vital-red/8 p-5">
        <div className="mb-3 flex items-center gap-2.5">
          <TriangleAlert size={14} strokeWidth={2.2} className="text-vital-red" />
          <p className="type-label text-vital-red">Allergies</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {["Penicillin", "Dust mites"].map((a) => (
            <span key={a} className="rounded-full bg-vital-red/12 px-3 py-1 text-[14px] font-bold text-vital-red">{a}</span>
          ))}
        </div>
      </motion.div>

      <motion.div variants={riseIn} className="rounded-lg2 border border-line bg-card p-5 shadow-soft">
        <p className="type-label mb-4 text-fg-muted">Connected</p>
        {[
          { icon: Watch, name: "Apple Watch Series 9", status: "Syncing" },
          { icon: IdCard, name: "ABHA — ····1234", status: "Verified" },
          { icon: ShieldCheck, name: "Star Health · Family Floater", status: "Active" },
        ].map((d) => (
          <div key={d.name} className="flex items-center gap-3 border-t border-line py-3 first:border-0 first:pt-0">
            <d.icon size={16} strokeWidth={1.9} className="shrink-0 text-fg-muted" />
            <p className="min-w-0 flex-1 truncate text-[15px] text-fg-soft">{d.name}</p>
            <Badge tone="green" dot>{d.status}</Badge>
          </div>
        ))}
      </motion.div>

      <motion.div variants={riseIn} className="rounded-lg2 border border-line bg-card p-5 shadow-soft">
        <p className="type-label mb-4 text-fg-muted">Lifestyle</p>
        {[
          { label: "Hydration", pct: 40, tone: "red", note: "1.2 / 3.0 L" },
          { label: "Sleep", pct: 71, tone: "amber", note: "6.4 hrs avg" },
          { label: "Activity", pct: 62, tone: "green", note: "6,240 steps" },
        ].map((l) => (
          <div key={l.label} className="mb-4 last:mb-0">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-[15px] font-bold text-fg-soft">{l.label}</p>
              <p className="tabular text-[14px] text-fg-muted">{l.note}</p>
            </div>
            <Progress value={l.pct} tone={l.tone} />
          </div>
        ))}
      </motion.div>
    </motion.div>
  );
}

/* ═══ PAGE ═════════════════════════════════════════════════════ */

export default function Profile() {
  const stageRef = useRef(null);
  const [selected, setSelected] = useState(null);
  const [isolate, setIsolate] = useState(false);
  const [visibleSystems, setVisibleSystems] = useState(
    Object.fromEntries(SYSTEMS.map((s) => [s.id, s.on]))
  );

  /* parallax tilt */
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 60, damping: 20 });
  const sy = useSpring(my, { stiffness: 60, damping: 20 });
  const rotX = useTransform(sy, [-1, 1], [6, -6]);
  const rotY = useTransform(sx, [-1, 1], [-8, 8]);

  const onMove = (e) => {
    const r = stageRef.current.getBoundingClientRect();
    mx.set(((e.clientX - r.left) / r.width) * 2 - 1);
    my.set(((e.clientY - r.top) / r.height) * 2 - 1);
  };
  const reset = () => { mx.set(0); my.set(0); };

  const anomaly = ORGANS.find((o) => o.risk === "high");
  const shown = ORGANS.filter((o) => visibleSystems[o.system] ?? true);

  return (
    <motion.div variants={cascade(0.08)} initial="initial" animate="animate">
      <motion.header variants={riseIn} className="mb-10">
        <p className="type-eyebrow mb-4 text-fg-muted">Health Profile</p>
        <h1 className="type-mega text-fg">
          Your body, <em className="serif">annotated</em>.
        </h1>
        <p className="mt-4 max-w-[600px] text-[18px] leading-relaxed text-fg-soft">
          Every organ carries its own reports, notes, risk and timeline. Click any marker.
        </p>
      </motion.header>

      <div className="grid gap-5 xl:grid-cols-12">
        <motion.section
          variants={riseIn}
          className="relative overflow-hidden rounded-card border border-line bg-card p-7 shadow-soft xl:col-span-8"
        >
          {/* system toggles + isolate */}
          <div className="no-scrollbar mb-6 flex items-center gap-2 overflow-x-auto">
            {SYSTEMS.map((s) => {
              const on = visibleSystems[s.id];
              return (
                <button
                  key={s.id}
                  onClick={() => setVisibleSystems((v) => ({ ...v, [s.id]: !v[s.id] }))}
                  className={cn(
                    "flex items-center gap-2 whitespace-nowrap rounded-full border px-4 py-2 text-[15px] font-bold transition-all",
                    on
                      ? "border-navy-700/30 bg-brand-soft text-navy-700"
                      : "border-line text-fg-muted hover:text-fg"
                  )}
                >
                  {on ? <Eye size={14} /> : <EyeOff size={14} />}
                  {s.label}
                </button>
              );
            })}
            <span className="mx-1 h-6 w-px shrink-0 bg-line" />
            <button
              onClick={() => setIsolate((i) => !i)}
              className={cn(
                "whitespace-nowrap rounded-full border px-4 py-2 text-[15px] font-bold transition-all",
                isolate
                  ? "border-vital-red/40 bg-vital-red/10 text-vital-red"
                  : "border-line text-fg-muted hover:text-fg"
              )}
            >
              Isolate findings
            </button>
          </div>

          {/* stage */}
          <div
            ref={stageRef}
            onMouseMove={onMove}
            onMouseLeave={reset}
            className="relative mx-auto aspect-[3/5] w-full max-w-[460px]"
            style={{ perspective: 1100 }}
          >
            <div className="absolute inset-0 rounded-[32px] bg-gradient-to-b from-surface/70 via-transparent to-surface/70" />
            <div className="absolute left-1/2 top-1/2 h-[70%] w-[70%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-azure-200/25 blur-[80px] dark:bg-azure-500/10" />

            <motion.div
              style={{ rotateX: rotX, rotateY: rotY, transformStyle: "preserve-3d" }}
              className="relative h-full w-full"
            >
              {/* THE RENDER */}
              <img
                src="/assets/illustrations/anatomy-front.png"
                alt="Human anatomy"
                onError={(e) => { e.currentTarget.style.display = "none"; }}
                className="relative z-10 mx-auto h-full w-full object-contain"
                style={{ transform: "translateZ(0px)" }}
                draggable={false}
              />

              {/* placeholder — visible only while asset is absent */}
              <div className="pointer-events-none absolute inset-0 z-0 grid place-items-center">
                <div className="mx-6 rounded-[24px] border-2 border-dashed border-line-strong px-8 py-10 text-center">
                  <Scan size={34} strokeWidth={1.3} className="mx-auto mb-4 text-fg-muted" />
                  <p className="type-label mb-2 text-fg-muted">Anatomy Render</p>
                  <p className="mx-auto max-w-[220px] text-[14px] leading-relaxed text-fg-muted">
                    Drop a transparent PNG at
                    <span className="mt-1.5 block font-bold text-fg-soft">
                      /public/assets/illustrations/<br />anatomy-front.png
                    </span>
                  </p>
                </div>
              </div>

              {/* hotspots — depth-layered above the body */}
              {shown.map((o) => (
                <Hotspot
                  key={o.id}
                  organ={o}
                  active={selected?.id === o.id}
                  dimmed={isolate && o.risk === "low"}
                  onClick={() => setSelected(selected?.id === o.id ? null : o)}
                />
              ))}

              {/* scan sweep */}
              <motion.span
                className="pointer-events-none absolute inset-x-8 z-10 h-px bg-gradient-to-r from-transparent via-navy-700/40 to-transparent"
                animate={{ top: ["8%", "92%", "8%"] }}
                transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
                style={{ transform: "translateZ(24px)" }}
              />
            </motion.div>

            {/* anomaly leader card */}
            {anomaly && !selected && (
              <AnomalyCallout organ={anomaly} onOpen={() => setSelected(anomaly)} />
            )}
          </div>

          {/* legend */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-5 border-t border-line pt-5">
            {[
              { hex: RISK_HEX.low, label: "Normal", n: shown.filter((o) => o.risk === "low").length },
              { hex: RISK_HEX.medium, label: "Watch", n: shown.filter((o) => o.risk === "medium").length },
              { hex: RISK_HEX.high, label: "Active concern", n: shown.filter((o) => o.risk === "high").length },
            ].map((r) => (
              <span key={r.label} className="flex items-center gap-2 text-[14px] text-fg-muted">
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: r.hex }} />
                {r.label}
                <span className="tabular font-bold text-fg-soft">{r.n}</span>
              </span>
            ))}
          </div>

          <AnimatePresence>
            {selected && <OrganPanel organ={selected} onClose={() => setSelected(null)} />}
          </AnimatePresence>
        </motion.section>

        <div className="xl:col-span-4">
          <MetricsRail />
        </div>
      </div>
    </motion.div>
  );
}