import { useRef } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { HeartPulse, Droplets, Activity, ShieldCheck, Car } from "lucide-react";
import Logo from "../brand/Logo";
import { cascade, riseIn, EASE } from "../../lib/motion";

/**
 * The brand world. A powdered field that responds to the cursor.
 * Layers move at different depths; cards drift; the ECG redraws itself.
 *
 * The wordmark carries the brand. Nothing else needs to.
 */
export default function AuthAside({ variant = "login" }) {
  const ref = useRef(null);

  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 65, damping: 22 });
  const sy = useSpring(my, { stiffness: 65, damping: 22 });

  const bgX = useTransform(sx, [-1, 1], [14, -14]);
  const bgY = useTransform(sy, [-1, 1], [11, -11]);
  const midX = useTransform(sx, [-1, 1], [-24, 24]);
  const midY = useTransform(sy, [-1, 1], [-17, 17]);
  const frontX = useTransform(sx, [-1, 1], [-42, 42]);
  const frontY = useTransform(sy, [-1, 1], [-28, 28]);
  const tiltX = useTransform(sy, [-1, 1], [7, -7]);
  const tiltY = useTransform(sx, [-1, 1], [-9, 9]);

  const onMove = (e) => {
    const r = ref.current.getBoundingClientRect();
    mx.set(((e.clientX - r.left) / r.width) * 2 - 1);
    my.set(((e.clientY - r.top) / r.height) * 2 - 1);
  };
  const reset = () => { mx.set(0); my.set(0); };

  const copy = {
    login: {
      title: "Your entire health,\nfinally in <em>one</em> place.",
      body: "Wearables, records, doctors, pharmacy, rides and care — connected, understood, and always with you.",
    },
    register: {
      title: "A profile that\n<em>actually</em> knows you.",
      body: "Four short steps. Every insight after this is built on what you tell us here.",
    },
  }[variant];

  return (
    <aside
      ref={ref}
      onMouseMove={onMove}
      onMouseLeave={reset}
      className="relative hidden w-[47%] max-w-[760px] overflow-hidden lg:block
                 bg-gradient-to-br from-powder-200 via-mist-100 to-sand-100"
    >
      {/* Depth 0 — mesh and light blooms */}
      <motion.div style={{ x: bgX, y: bgY }} className="absolute inset-[-6%]">
        <div className="absolute inset-0 grid-mesh opacity-70" />
        <motion.div
          animate={{ scale: [1, 1.15, 1], opacity: [0.5, 0.75, 0.5] }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -left-24 top-[4%] h-[460px] w-[460px] rounded-full bg-powder-400/50 blur-[130px]"
        />
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.4, 0.62, 0.4] }}
          transition={{ duration: 14, repeat: Infinity, ease: "easeInOut", delay: 2.5 }}
          className="absolute -right-20 bottom-[4%] h-[500px] w-[500px] rounded-full bg-sand-200/70 blur-[140px]"
        />
        <motion.div
          animate={{ y: [0, -28, 0] }}
          transition={{ duration: 17, repeat: Infinity, ease: "easeInOut" }}
          className="absolute left-1/3 top-1/3 h-[320px] w-[320px] rounded-full bg-vital-teal/14 blur-[110px]"
        />
      </motion.div>

      {/* Motes */}
      {[...Array(16)].map((_, i) => (
        <motion.span
          key={i}
          className="absolute h-1 w-1 rounded-full bg-ink-700/20"
          style={{ left: `${(i * 37) % 92 + 4}%`, top: `${(i * 53) % 88 + 6}%` }}
          animate={{ y: [0, -28, 0], opacity: [0, 0.85, 0] }}
          transition={{
            duration: 7 + (i % 5),
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.5,
          }}
        />
      ))}

      <motion.div
        variants={cascade(0.13, 0.15)}
        initial="initial"
        animate="animate"
        className="relative flex h-full flex-col justify-between p-12 xl:p-16"
      >
        <motion.div variants={riseIn}>
          <Logo size="lg" tagline />
        </motion.div>

        {/* Illustration stage */}
        <div className="relative my-8 flex flex-1 items-center justify-center">
          <motion.div
            style={{
              x: midX, y: midY,
              rotateX: tiltX, rotateY: tiltY,
              transformPerspective: 1000,
            }}
            variants={riseIn}
            className="relative grid h-[320px] w-[320px] place-items-center xl:h-[360px] xl:w-[360px]"
          >
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="absolute rounded-full border border-dashed border-ink-700/16"
                style={{ inset: `${i * 36}px` }}
                animate={{ rotate: i % 2 === 0 ? 360 : -360 }}
                transition={{ duration: 42 + i * 16, repeat: Infinity, ease: "linear" }}
              >
                <span className="absolute left-1/2 top-0 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-ink-700 shadow-[0_0_14px_2px_rgba(44,66,112,0.45)]" />
              </motion.span>
            ))}

            <motion.span
              animate={{ scale: [1, 1.3, 1], opacity: [0.26, 0, 0.26] }}
              transition={{ duration: 3.2, repeat: Infinity, ease: "easeOut" }}
              className="absolute h-44 w-44 rounded-[48px] bg-ink-700/20 blur-2xl"
            />

            <motion.div
              animate={{ scale: [1, 1.04, 1] }}
              transition={{ duration: 3.6, repeat: Infinity, ease: "easeInOut" }}
              className="relative grid h-44 w-44 place-items-center overflow-hidden rounded-[46px] border border-white/80 bg-white/65 shadow-float backdrop-blur-2xl xl:h-48 xl:w-48"
            >
              <HeartPulse size={64} strokeWidth={1.1} className="text-ink-700" />

              <svg viewBox="0 0 160 40" className="absolute bottom-6 h-8 w-32 overflow-visible" fill="none">
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

          <motion.div style={{ x: frontX, y: frontY }} className="absolute inset-0">
            <FloatCard icon={Activity} label="Heart Rate" value="72 bpm" tone="text-vital-red" className="left-0 top-4" delay={0} />
            <FloatCard icon={Droplets} label="Hydration" value="2.1 / 3.0 L" tone="text-vital-teal" className="bottom-14 left-6" delay={1.3} />
            <FloatCard icon={ShieldCheck} label="ABHA Linked" value="Verified" tone="text-vital-green" className="right-0 top-20" delay={0.7} />
            <FloatCard icon={Car} label="Ride to Clinic" value="Uber · 6 min" tone="text-ink-700" className="bottom-6 right-2" delay={2} />
          </motion.div>
        </div>

        {/* Copy */}
        <motion.div variants={riseIn} className="max-w-[520px]">
          <h2
            className="type-hero whitespace-pre-line text-fg"
            dangerouslySetInnerHTML={{ __html: copy.title }}
          />
          <p className="mt-6 max-w-[430px] text-[17px] leading-relaxed text-fg-soft">
            {copy.body}
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-3 border-t border-ink-700/12 pt-7">
            {["One Health.", "One Intelligence.", "One Ecosystem."].map((t, i) => (
              <motion.span
                key={t}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 + i * 0.14, duration: 0.5, ease: EASE }}
                className="flex items-center gap-3"
              >
                {i > 0 && <span className="h-1 w-1 rounded-full bg-fg-muted/50" />}
                <span className="text-[16px] font-bold text-fg-soft">{t}</span>
              </motion.span>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </aside>
  );
}

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
      className={`absolute flex cursor-default items-center gap-3 rounded-[18px] border border-white/80 bg-white/72 px-4 py-3 shadow-soft backdrop-blur-xl ${className}`}
    >
      <span className={`grid h-8 w-8 place-items-center rounded-[10px] bg-white/80 ${tone}`}>
        <Icon size={15} strokeWidth={2} />
      </span>
      <div className="leading-tight">
        <p className="text-[10.5px] font-bold uppercase tracking-[0.12em] text-fg-muted">{label}</p>
        <p className="mt-0.5 text-[14px] font-bold text-fg">{value}</p>
      </div>
    </motion.div>
  );
}