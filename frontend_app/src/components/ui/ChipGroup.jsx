import { motion } from "framer-motion";
import { cn } from "../../lib/cn";

/** Segmented chips — used across onboarding for single-choice lifestyle answers. */
export default function ChipGroup({ label, options = [], value, onChange, className }) {
  return (
    <div className={cn("w-full", className)}>
      {label && <label className="mb-2.5 block text-[13px] font-medium text-fg-soft">{label}</label>}
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const active = value === opt;
          return (
            <motion.button
              key={opt}
              type="button"
              whileTap={{ scale: 0.96 }}
              onClick={() => onChange?.(opt)}
              className={cn(
                "rounded-full border px-4 py-2 text-[13.5px] font-medium transition-all duration-200",
                active
                  ? "border-transparent bg-navy-700 text-white shadow-soft dark:bg-azure-500 dark:text-navy-950"
                  : "border-line bg-card text-fg-soft hover:border-line-strong hover:text-fg"
              )}
            >
              {opt}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
