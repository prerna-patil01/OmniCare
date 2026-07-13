import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

/** Generic anchored dropdown — used by the profile menu and notifications. */
export default function Dropdown({ trigger, children, align = "right", width = "w-64", className }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const onDoc = (e) => ref.current && !ref.current.contains(e.target) && setOpen(false);
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  return (
    <div className={cn("relative", className)} ref={ref}>
      <div onClick={() => setOpen((o) => !o)}>{trigger}</div>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.97 }}
            animate={{ opacity: 1, y: 10, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.97 }}
            transition={{ duration: 0.24, ease: EASE }}
            className={cn(
              "absolute z-50 origin-top rounded-[20px] border border-line bg-card p-2 shadow-lift",
              align === "right" ? "right-0" : "left-0",
              width
            )}
            onClick={() => setOpen(false)}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function DropdownItem({ icon: Icon, children, onClick, tone = "default" }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-3 rounded-[12px] px-3 py-2.5 text-left text-[14px] transition-colors",
        tone === "danger"
          ? "text-vital-red hover:bg-vital-red/8"
          : "text-fg-soft hover:bg-mist-50 hover:text-fg dark:hover:bg-navy-800"
      )}
    >
      {Icon && <Icon size={16} strokeWidth={1.9} />}
      {children}
    </button>
  );
}

export function DropdownDivider() {
  return <div className="my-2 h-px bg-line" />;
}
