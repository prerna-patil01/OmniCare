import { useEffect } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

export default function Modal({ open, onClose, title, subtitle, children, footer, size = "md" }) {
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose?.();
    if (open) {
      document.addEventListener("keydown", onKey);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  const widths = { sm: "max-w-md", md: "max-w-xl", lg: "max-w-3xl" };

  return createPortal(
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[100] grid place-items-center p-5">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            onClick={onClose}
            className="absolute inset-0 bg-navy-950/45 backdrop-blur-sm"
          />
          <motion.div
            initial={{ opacity: 0, y: 24, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.98 }}
            transition={{ duration: 0.35, ease: EASE }}
            className={cn(
              "relative w-full rounded-xl2 border border-line bg-card shadow-lift",
              widths[size]
            )}
          >
            <div className="flex items-start justify-between gap-6 px-8 pb-5 pt-7">
              <div>
                <h3 className="font-display text-[24px] font-semibold tracking-[-0.015em] text-fg">
                  {title}
                </h3>
                {subtitle && <p className="mt-1.5 text-[14px] text-fg-muted">{subtitle}</p>}
              </div>
              <button
                onClick={onClose}
                className="grid h-9 w-9 shrink-0 place-items-center rounded-full text-fg-muted transition-colors hover:bg-mist-100 hover:text-fg dark:hover:bg-navy-800"
                aria-label="Close"
              >
                <X size={17} />
              </button>
            </div>
            <div className="px-8 pb-8">{children}</div>
            {footer && (
              <div className="flex justify-end gap-3 border-t border-line px-8 py-5">{footer}</div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>,
    document.body
  );
}
