import { useRef } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { HeartPulse, Droplets, Activity, ShieldCheck, Car } from "lucide-react";
import Logo from "../brand/Logo";
import { cascade, riseIn, EASE } from "../../lib/motion";

/**
 * The brand panel — a powdered-blue field that responds to the cursor.
 * Layers move at different depths (parallax), the ECG trace redraws itself,
 * orbit rings drift, and every card breathes. Nothing here is static.
 *
 * The central core is a PLACEHOLDER: drop a high-fidelity medical render into
 * /public/assets/illustrations/auth-hero.png and swap the <HeartPulse> for an <img>.
 */
export default function AuthAside({ variant = "login" }) {
  const ref = useRef(null);

  // ── Cursor parallax ──────────────────────────────────────────
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 70, damping: 22 });
  const sy = useSpring(my, { stiffness: 70, damping: 22 });

  // Depth layers: background drifts least, foreground cards drift most.
  const bgX = useTransform(sx, [-1, 1], [12, -12]);
  const bgY = useTransform(sy, [-1, 1], [10, -10]);
  const midX = useTransform(sx, [-1, 1], [-22, 22]);
  const midY = useTransform(sy, [-1, 1], [-16, 16]);
  const frontX = useTransform(sx, [-1, 1], [-38, 38]);
  const frontY = useTransform(sy, [-1, 1], [-26, 26]);
  const tiltX = useTransform(sy, [-1, 1], [7, -7]);
  const tiltY = useTransform(sx, [-1, 1], [-9, 9]);

  const onMove = (e) => {
    const r = ref.current.getBoundingClientRect();
    mx.set(((e.clientX - r.left) / r.width) * 2 - 1);
    my.set(((e.clientY - r.top) / r.height) * 2 - 1);
  };

  const reset = () => {
    mx.set(0);
    my.set(0);
  };

  const copy = {
    login: {
      eyebrow: "Healthcare Operating System",
      title: "Your entire health,\nfinally in one place.",
      body: "Wearables, records, doctors, pharmacy, rides and care — connected, understood, and always with you.",
    },
    register: {
      eyebrow: "Set up your health identity",
      title: "A profile that\nactually knows you.",
      body: "Four short steps. Every insight after this is built on what you tell us here.",
    },
  }[variant];

  return (
    <aside
      ref={ref}
      onMouseMove={onMove}
      onMouseLeave={reset}
      className="relative hidden w-[46%] max-w-[720px] overflow-hidden lg:block
                 bg-gradient-to-br from-azure-100 via-mist-100 to-sand-100
                 dark:from-navy-900 dark:via-[#243350] dark:to-[#1E2B44]"
    >
      {/* ── Depth 0 — mesh + soft light blooms ─────────────────── */}
      <motion.div style={{ x: bgX, y: bgY }} className="absolute inset-[-6%]">
        <div className="absolute inset-0 grid-mesh opacity-70" />
        <motion.div
          animate={{ scale: [1, 1.14, 1], opacity: [0.5, 0.72, 0.5] }}
          transition={{ duration: 11, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -left-24 top-[6%] h-[440px] w-[440px] rounded-full bg-azure-300/45 blur-[130px]"
        />
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.42, 0.62, 0.42] }}
          transition={{ duration: 13, repeat: Infinity, ease: "easeInOut", delay: 2.5 }}
          className="absolute -right-20 bottom-[4%] h-[480px] w-[480px] rounded-full bg-sand-200/60 blur-[140px] dark:bg-azure-500/25"
        />
        <motion.div
          animate={{ y: [0, -26, 0] }}
          transition={{ duration: 16, repeat: Infinity, ease: "easeInOut" }}
          className="absolute left-1/3 top-1/3 h-[300px] w-[300px] rounded-full bg-vital-teal/16 blur-[110px]"
        />
      </motion.div>

      {/* ── Drifting motes ─────────────────────────────────────── */}
      {[...Array(14)].map((_, i) => (
        <motion.span
          key={i}
          className="absolute h-1 w-1 rounded-full bg-navy-700/22 dark:bg-azure-300/28"
          style={{ left: `${(i * 37) % 92 + 4}%`, top: `${(i * 53) % 88 + 6}%` }}
          animate={{ y: [0, -26, 0], opacity: [0, 0.9, 0] }}
          transition={{
            duration: 7 + (i % 5),
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.55,
          }}
        />
      ))}

      <motion.div
        variants={cascade(0.12, 0.15)}
        initial="initial"
        animate="animate"
        className="relative flex h-full flex-col justify-between p-12 xl:p-16"
      >
        <motion.div variants={riseIn}>
          <Logo size={44} />
        </motion.div>

        {/* ── Illustration stage ───────────────────────────────── */}
        <div className="relative my-10 flex flex-1 items-center justify-center">
          {/* Depth 1 — orbit + core */}
          <motion.div
            style={{ x: midX, y: midY, rotateX: tiltX, rotateY: tiltY, transformPerspective: 1000 }}
            variants={riseIn}
            className="relative grid h-[320px] w-[320px] place-items-center xl:h-[360px] xl:w-[360px]"
          >
            {/* orbit rings — counter-rotating, dashed */}
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="absolute rounded-full border border-dashed border-navy-700/16 dark:border-azure-300/18"
                style={{ inset: `${i * 36}px` }}
                animate={{ rotate: i % 2 === 0 ? 360 : -360 }}
                transition={{ duration: 40 + i * 16, repeat: Infinity, ease: "linear" }}
              >
                {/* a node riding each ring */}
                <span
                  className="absolute left-1/2 top-0 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full
                             bg-navy-700 shadow-[0_0_14px_2px_rgba(74,114,178,0.5)] dark:bg-azure-300"
                />
              </motion.span>
            ))}

            {/* halo */}
            <motion.span
              animate={{ scale: [1, 1.28, 1], opacity: [0.28, 0, 0.28] }}
              transition={{ duration: 3.2, repeat: Infinity, ease: "easeOut" }}
              className="absolute h-44 w-44 rounded-[48px] bg-navy-700/22 blur-2xl dark:bg-azure-400/25"
            />

            {/* core card — replace with the real render */}
            <motion.div
              animate={{ scale: [1, 1.04, 1] }}
              transition={{ duration: 3.6, repeat: Infinity, ease: "easeInOut" }}
              className="relative grid h-44 w-44 place-items-center overflow-hidden rounded-[46px]
                         border border-white/70 bg-white/60 shadow-glow backdrop-blur-2xl
                         dark:border-white/10 dark:bg-white/[0.07] xl:h-48 xl:w-48"
            >
              <HeartPulse
                size={64}
                strokeWidth={1.15}
                className="text-navy-700 dark:text-azure-200"
              />

              {/* animated ECG trace beneath the heart */}
              <svg
                viewBox="0 0 160 40"
                className="absolute bottom-6 h-8 w-32 overflow-visible"
                fill="none"
              >
                <motion.path
                  d="M0 20 H30 L38 20 L44 6 L52 34 L60 14 L66 20 H96 L104 20 L110 10 L118 30 L124 20 H160"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="text-vital-red/85"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: [0, 1, 1], opacity: [0, 1, 0] }}
                  transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
                />
              </svg>
            </motion.div>
          </motion.div>

          {/* Depth 2 — floating live cards */}
          <motion.div style={{ x: frontX, y: frontY }} className="absolute inset-0">
            <FloatCard
              icon={Activity}
              label="Heart Rate"
              value="72 bpm"
              tone="text-vital-red"
              className="left-0 top-4"
              delay={0}
            />
            <FloatCard
              icon={Droplets}
              label="Hydration"
              value="2.1 / 3.0 L"
              tone="text-vital-teal"
              className="bottom-14 left-6"
              delay={1.3}
            />
            <FloatCard
              icon={ShieldCheck}
              label="ABHA Linked"
              value="Verified"
              tone="text-vital-green"
              className="right-0 top-20"
              delay={0.7}
            />
            <FloatCard
              icon={Car}
              label="Ride to Clinic"
              value="Uber · 6 min"
              tone="text-navy-700 dark:text-azure-300"
              className="bottom-6 right-2"
              delay={2}
            />
          </motion.div>
        </div>

        {/* ── Copy ─────────────────────────────────────────────── */}
        <motion.div variants={riseIn} className="max-w-[440px]">
          <p className="mb-4 text-[11px] font-semibold uppercase tracking-[0.22em] text-navy-700 dark:text-azure-300">
            {copy.eyebrow}
          </p>
          <h2 className="whitespace-pre-line font-display text-[38px] font-semibold leading-[1.14] tracking-[-0.025em] text-fg xl:text-[43px]">
            {copy.title}
          </h2>
          <p className="mt-5 max-w-[410px] text-[15px] leading-relaxed text-fg-soft">
            {copy.body}
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-3 border-t border-navy-700/12 pt-7 dark:border-white/10">
            {["One Health.", "One Intelligence.", "One Ecosystem."].map((t, i) => (
              <motion.span
                key={t}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 + i * 0.13, duration: 0.5, ease: EASE }}
                className="flex items-center gap-3"
              >
                {i > 0 && <span className="h-1 w-1 rounded-full bg-fg-muted/50" />}
                <span className="text-[13px] font-medium text-fg-soft">{t}</span>
              </motion.span>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </aside>
  );
}

/** Glass metric card — drifts on its own, lifts under the cursor. */
function FloatCard({ icon: Icon, label, value, tone, className, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 22, scale: 0.88 }}
      animate={{ opacity: 1, scale: 1, y: [0, -10, 0] }}
      transition={{
        opacity: { duration: 0.6, delay: 0.5 + delay, ease: EASE },
        scale: { duration: 0.6, delay: 0.5 + delay, ease: EASE },
        y: { duration: 5.5, repeat: Infinity, ease: "easeInOut", delay },
      }}
      whileHover={{ scale: 1.06, y: -14, transition: { duration: 0.3, ease: EASE } }}
      className={`absolute flex cursor-default items-center gap-3 rounded-[18px] border border-white/70
                  bg-white/70 px-4 py-3 shadow-soft backdrop-blur-xl
                  dark:border-white/10 dark:bg-white/[0.07] ${className}`}
    >
      <span className={`grid h-8 w-8 place-items-center rounded-[10px] bg-white/70 dark:bg-white/10 ${tone}`}>
        <Icon size={15} strokeWidth={2} />
      </span>
      <div className="leading-tight">
        <p className="text-[10.5px] font-medium uppercase tracking-[0.1em] text-fg-muted">{label}</p>
        <p className="mt-0.5 text-[13.5px] font-semibold text-fg">{value}</p>
      </div>
    </motion.div>
  );
}