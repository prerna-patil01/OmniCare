import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Command } from "lucide-react";
import { cn } from "../../lib/cn";

export default function UniversalSearch({ className }) {
  const [focused, setFocused] = useState(false);

  return (
    <motion.div
      animate={{ scale: focused ? 1.01 : 1 }}
      transition={{ duration: 0.25 }}
      className={cn(
        "flex h-11 items-center gap-3 rounded-full border bg-card px-4 transition-all duration-250",
        focused
          ? "border-azure-500/70 ring-4 ring-azure-500/12"
          : "border-line hover:border-line-strong",
        className
      )}
    >
      <Search size={16} strokeWidth={2} className="shrink-0 text-fg-muted" />
      <input
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder="Search doctors, records, medicines, symptoms…"
        className="w-full bg-transparent text-[14px] text-fg outline-none placeholder:text-fg-muted/75"
      />
      <span className="hidden shrink-0 items-center gap-0.5 rounded-md border border-line px-1.5 py-0.5 text-[10.5px] font-medium text-fg-muted md:flex">
        <Command size={10} /> K
      </span>
    </motion.div>
  );
}
