import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { cn } from "../../lib/cn";

export default function Checkbox({ checked, onChange, label, className }) {
  return (
    <button
      type="button"
      onClick={() => onChange?.(!checked)}
      className={cn("group flex items-center gap-2.5 text-left", className)}
    >
      <span
        className={cn(
          "grid h-[19px] w-[19px] shrink-0 place-items-center rounded-[6px] border transition-all duration-200",
          checked
            ? "border-navy-700 bg-navy-700 dark:border-azure-500 dark:bg-azure-500"
            : "border-line-strong bg-card group-hover:border-navy-700/50"
        )}
      >
        <motion.span
          initial={false}
          animate={{ scale: checked ? 1 : 0, opacity: checked ? 1 : 0 }}
          transition={{ duration: 0.18 }}
          className="text-white dark:text-navy-950"
        >
          <Check size={12} strokeWidth={3.2} />
        </motion.span>
      </span>
      {label && <span className="text-[13.5px] text-fg-soft">{label}</span>}
    </button>
  );
}
