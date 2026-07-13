import { motion } from "framer-motion";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

export default function Progress({ value = 0, className, tone = "brand" }) {
  const tones = {
    brand: "bg-navy-700 dark:bg-azure-500",
    green: "bg-vital-green",
    amber: "bg-vital-amber",
    red: "bg-vital-red",
  };
  return (
    <div className={cn("h-1.5 w-full overflow-hidden rounded-full bg-mist-200 dark:bg-navy-800", className)}>
      <motion.div
        className={cn("h-full rounded-full", tones[tone])}
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        transition={{ duration: 0.7, ease: EASE }}
      />
    </div>
  );
}
