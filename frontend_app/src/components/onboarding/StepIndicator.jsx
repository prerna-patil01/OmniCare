import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

export default function StepIndicator({ steps, current }) {
  const pct = (current / (steps.length - 1)) * 100;

  return (
    <div className="mb-10">
      {/* rail */}
      <div className="relative mb-6">
        <div className="absolute left-0 right-0 top-[15px] h-[2px] rounded-full bg-mist-200 dark:bg-navy-800" />
        <motion.div
          className="absolute left-0 top-[15px] h-[2px] rounded-full bg-navy-700 dark:bg-azure-500"
          initial={false}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.55, ease: EASE }}
        />

        <ol className="relative flex justify-between">
          {steps.map((s, i) => {
            const done = i < current;
            const active = i === current;
            return (
              <li key={s.label} className="flex flex-col items-center">
                <motion.span
                  animate={{ scale: active ? 1.06 : 1 }}
                  transition={{ duration: 0.3, ease: EASE }}
                  className={cn(
                    "grid h-8 w-8 place-items-center rounded-full border-2 text-[12px] font-semibold transition-colors duration-300",
                    done
                      ? "border-navy-700 bg-navy-700 text-white dark:border-azure-500 dark:bg-azure-500 dark:text-navy-950"
                      : active
                      ? "border-navy-700 bg-card text-navy-700 shadow-soft dark:border-azure-500 dark:text-azure-300"
                      : "border-mist-300 bg-card text-fg-muted dark:border-navy-800"
                  )}
                >
                  {done ? <Check size={14} strokeWidth={3} /> : i + 1}
                </motion.span>
              </li>
            );
          })}
        </ol>
      </div>

      <div className="flex justify-between">
        {steps.map((s, i) => (
          <p
            key={s.label}
            className={cn(
              "w-[25%] text-center text-[12px] font-medium transition-colors duration-300 sm:text-[13px]",
              i === current ? "text-fg" : "text-fg-muted"
            )}
          >
            {s.label}
          </p>
        ))}
      </div>
    </div>
  );
}
