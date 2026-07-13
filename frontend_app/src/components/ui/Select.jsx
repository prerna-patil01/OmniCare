import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Check, AlertCircle } from "lucide-react";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

/** Custom select — native selects cannot carry the OmniCare radius/motion language. */
export default function Select({
  label,
  value,
  onChange,
  options = [],
  placeholder = "Select",
  error,
  icon: Icon,
  className,
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const onDoc = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const selected = options.find((o) => (o.value ?? o) === value);
  const labelOf = (o) => (typeof o === "string" ? o : o.label);
  const valueOf = (o) => (typeof o === "string" ? o : o.value);

  return (
    <div className={cn("w-full", className)} ref={ref}>
      {label && (
        <label className="mb-2 block text-[13px] font-medium text-fg-soft">{label}</label>
      )}

      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={cn(
          "relative flex h-[52px] w-full items-center gap-3 rounded-[16px] border bg-card px-4 text-left transition-all duration-250",
          error
            ? "border-vital-red/60 ring-4 ring-vital-red/10"
            : open
            ? "border-azure-500/70 ring-4 ring-azure-500/12"
            : "border-line hover:border-line-strong"
        )}
      >
        {Icon && <Icon size={17} strokeWidth={1.9} className="text-fg-muted" />}
        <span className={cn("flex-1 truncate text-[15px]", selected ? "text-fg" : "text-fg-muted/70")}>
          {selected ? labelOf(selected) : placeholder}
        </span>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.25, ease: EASE }}
          className="text-fg-muted"
        >
          <ChevronDown size={17} />
        </motion.span>
      </button>

      <div className="relative">
        <AnimatePresence>
          {open && (
            <motion.ul
              initial={{ opacity: 0, y: -6, scale: 0.985 }}
              animate={{ opacity: 1, y: 8, scale: 1 }}
              exit={{ opacity: 0, y: -6, scale: 0.985 }}
              transition={{ duration: 0.22, ease: EASE }}
              className="no-scrollbar absolute z-40 max-h-[336px] w-full overflow-y-auto rounded-[18px] border border-line bg-card p-1.5 shadow-lift"
            >
              {options.map((o) => {
                const v = valueOf(o);
                const active = v === value;
                return (
                  <li key={v}>
                    <button
                      type="button"
                      onClick={() => {
                        onChange?.(v);
                        setOpen(false);
                      }}
                      className={cn(
                        "flex w-full items-center justify-between rounded-[12px] px-3.5 py-2.5 text-left text-[14px] transition-colors",
                        active
                          ? "bg-brand-soft font-medium text-navy-700 dark:text-azure-300"
                          : "text-fg-soft hover:bg-mist-50 hover:text-fg dark:hover:bg-navy-800"
                      )}
                    >
                      {labelOf(o)}
                      {active && <Check size={15} />}
                    </button>
                  </li>
                );
              })}
            </motion.ul>
          )}
        </AnimatePresence>
      </div>

      {error && (
        <p className="mt-2 flex items-center gap-1.5 text-[12.5px] font-medium text-vital-red">
          <AlertCircle size={13} /> {error}
        </p>
      )}
    </div>
  );
}