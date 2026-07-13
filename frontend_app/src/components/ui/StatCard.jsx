import { motion } from "framer-motion";
import { cn } from "../../lib/cn";
import { riseIn, EASE } from "../../lib/motion";

export default function StatCard({ icon: Icon, label, value, unit, delta, tone = "neutral", className }) {
  const tones = {
    neutral: "text-navy-700 dark:text-azure-300 bg-brand-soft",
    green: "text-vital-green bg-vital-green/10",
    amber: "text-vital-amber bg-vital-amber/12",
    red: "text-vital-red bg-vital-red/10",
    teal: "text-vital-teal bg-vital-teal/10",
  };

  return (
    <motion.div
      variants={riseIn}
      whileHover={{ y: -4, transition: { duration: 0.28, ease: EASE } }}
      className={cn(
        "rounded-lg2 border border-line bg-card p-5 shadow-soft transition-shadow hover:shadow-lift",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className={cn("grid h-9 w-9 place-items-center rounded-[11px]", tones[tone])}>
          {Icon && <Icon size={16} strokeWidth={2} />}
        </span>
        {delta && <span className="text-[12px] font-semibold text-fg-muted">{delta}</span>}
      </div>
      <p className="mt-4 text-[12.5px] font-medium uppercase tracking-[0.08em] text-fg-muted">
        {label}
      </p>
      <p className="mt-1 font-display text-[26px] font-semibold tracking-[-0.02em] text-fg">
        {value}
        {unit && <span className="ml-1 text-[14px] font-medium text-fg-muted">{unit}</span>}
      </p>
    </motion.div>
  );
}
