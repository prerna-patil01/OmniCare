import { motion, AnimatePresence } from "framer-motion";
import { Sun, Moon } from "lucide-react";
import { useTheme } from "../../services/context/ThemeContext";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

export default function ThemeToggle({ className }) {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className={cn(
        "relative grid h-10 w-10 place-items-center overflow-hidden rounded-full border border-line bg-card text-fg-soft transition-colors hover:text-fg",
        className
      )}
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={isDark ? "moon" : "sun"}
          initial={{ y: 14, opacity: 0, rotate: -25 }}
          animate={{ y: 0, opacity: 1, rotate: 0 }}
          exit={{ y: -14, opacity: 0, rotate: 25 }}
          transition={{ duration: 0.32, ease: EASE }}
          className="absolute"
        >
          {isDark ? <Moon size={16} strokeWidth={1.9} /> : <Sun size={16} strokeWidth={1.9} />}
        </motion.span>
      </AnimatePresence>
    </button>
  );
}
