import { motion } from "framer-motion";
import { Apple, Activity, Watch, ShieldCheck, IdCard, Car, MapPin, Check, Plus } from "lucide-react";
import { cn } from "../../../lib/cn";
import { cascade, riseIn, EASE } from "../../../lib/motion";

const GROUPS = [
  {
    heading: "Health & Devices",
    items: [
      { id: "appleHealth", name: "Apple Health", desc: "Heart rate, HRV, sleep, steps, SpO₂", icon: Apple, accent: "text-fg" },
      { id: "googleFit", name: "Google Fit", desc: "Activity, calories, movement minutes", icon: Activity, accent: "text-vital-green" },
      { id: "smartWatch", name: "Smart Watch", desc: "Fitbit, Samsung Health, Wear OS", icon: Watch, accent: "text-azure-500" },
    ],
  },
  {
    heading: "Mobility",
    items: [
      { id: "uber", name: "Uber", desc: "One-tap ride to your clinic or lab", icon: Car, accent: "text-fg" },
      { id: "ola", name: "Ola", desc: "Ride booking with destination pre-filled", icon: Car, accent: "text-vital-amber" },
      { id: "maps", name: "Google Maps", desc: "Routing, ETA and nearby hospitals", icon: MapPin, accent: "text-vital-red" },
    ],
  },
  {
    heading: "Records & Coverage",
    items: [
      { id: "insurance", name: "Insurance", desc: "Policy, coverage, cashless network", icon: ShieldCheck, accent: "text-vital-teal" },
      { id: "abha", name: "ABHA ID", desc: "National health records interoperability", icon: IdCard, accent: "text-navy-700 dark:text-azure-300" },
    ],
  },
];

/** Connections turn a form into a living health profile. All optional. */
export default function ConnectionsStep({ data, update }) {
  const toggle = (id) =>
    update(
      "connections",
      data.connections.includes(id)
        ? data.connections.filter((c) => c !== id)
        : [...data.connections, id]
    );

  return (
    <motion.div variants={cascade(0.05)} initial="initial" animate="animate" className="grid gap-8">
      {GROUPS.map((group) => (
        <div key={group.heading}>
          <motion.p
            variants={riseIn}
            className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-fg-muted"
          >
            {group.heading}
          </motion.p>

          <div className="grid gap-3">
            {group.items.map((s) => {
              const connected = data.connections.includes(s.id);
              return (
                <motion.button
                  key={s.id}
                  variants={riseIn}
                  type="button"
                  whileHover={{ y: -3 }}
                  whileTap={{ scale: 0.995 }}
                  transition={{ duration: 0.25, ease: EASE }}
                  onClick={() => toggle(s.id)}
                  className={cn(
                    "flex items-center gap-4 rounded-lg2 border p-4.5 text-left transition-all duration-250",
                    connected
                      ? "border-navy-700/30 bg-brand-soft shadow-soft dark:border-azure-400/35"
                      : "border-line bg-card hover:border-line-strong hover:shadow-soft"
                  )}
                >
                  <span className={cn("grid h-11 w-11 shrink-0 place-items-center rounded-[13px] bg-surface", s.accent)}>
                    <s.icon size={19} strokeWidth={1.9} />
                  </span>

                  <div className="min-w-0 flex-1">
                    <p className="text-[15px] font-semibold text-fg">{s.name}</p>
                    <p className="mt-0.5 truncate text-[13px] text-fg-muted">{s.desc}</p>
                  </div>

                  <span
                    className={cn(
                      "grid h-8 w-8 shrink-0 place-items-center rounded-full transition-colors duration-250",
                      connected
                        ? "bg-navy-700 text-white dark:bg-azure-400 dark:text-navy-950"
                        : "bg-surface text-fg-muted"
                    )}
                  >
                    {connected ? <Check size={15} strokeWidth={3} /> : <Plus size={15} strokeWidth={2.4} />}
                  </span>
                </motion.button>
              );
            })}
          </div>
        </div>
      ))}

      <p className="text-center text-[12.5px] leading-relaxed text-fg-muted">
        Connect or disconnect any source later from{" "}
        <span className="font-medium text-fg-soft">Profile → Connected Devices</span>.
      </p>
    </motion.div>
  );
}