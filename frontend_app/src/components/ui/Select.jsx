import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Check, AlertCircle } from "lucide-react";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

/**
 * Custom select. Native selects can't carry the OmniCare radius/motion language.
 *
 * The list is deliberately tall (13 rows) — a truncated dropdown reads as a
 * short list, and users stop scrolling. Blood groups in particular MUST show
 * all options: a missed rare phenotype is a transfusion risk, not a UI nit.
 */
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
  const [scrolled, setScrolled] = useState(false);
  const ref = useRef(null);
  const listRef = useRef(null);

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

  /** True while there's still content below the fold — drives the fade hint. */
  const overflows = options.length > 7;

  return (
    <div className={cn("w-full", className)} ref={ref}>
      {label && <label className="mb-2 block text-[14px] font-bold text-fg-soft">{label}</label>}

      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={cn(
          "relative flex h-[54px] w-full items-center gap-3 rounded-[16px] border bg-card px-4 text-left transition-all duration-250",
          error
            ? "border-vital-red/60 ring-4 ring-vital-red/10"
            : open
            ? "border-azure-500/70 ring-4 ring-azure-500/12"
            : "border-line hover:border-line-strong"
        )}
      >
        {Icon && <Icon size={17} strokeWidth={1.9} className="text-fg-muted" />}
        <span className={cn("flex-1 truncate text-[16px]", selected ? "text-fg" : "text-fg-muted/70")}>
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
            <motion.div
              initial={{ opacity: 0, y: -6, scale: 0.985 }}
              animate={{ opacity: 1, y: 8, scale: 1 }}
              exit={{ opacity: 0, y: -6, scale: 0.985 }}
              transition={{ duration: 0.22, ease: EASE }}
              className="absolute z-0 w-full overflow-hidden rounded-[18px] border border-line bg-card shadow-lift"
            >
              <ul
                ref={listRef}
                onScroll={(e) => {
                  const el = e.currentTarget;
                  setScrolled(el.scrollTop + el.clientHeight >= el.scrollHeight - 8);
                }}
                className="no-scrollbar max-h-[420px] overflow-y-auto p-1.5"
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
                          "flex w-full items-center justify-between rounded-[12px] px-3.5 py-3 text-left text-[16px] transition-colors",
                          active
                            ? "bg-brand-soft font-bold text-navy-700"
                            : "text-fg-soft hover:bg-mist-50 hover:text-fg dark:hover:bg-navy-800"
                        )}
                      >
                        {labelOf(o)}
                        {active && <Check size={16} />}
                      </button>
                    </li>
                  );
                })}
              </ul>

              {/* Fade hint — tells the eye there's more below, without a scrollbar */}
              {overflows && !scrolled && (
                <div className="pointer-events-none absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-card to-transparent" />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {error && (
        <p className="mt-2 flex items-center gap-1.5 text-[13px] font-bold text-vital-red">
          <AlertCircle size={13} /> {error}
        </p>
      )}
    </div>
  );
}