import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Plus } from "lucide-react";
import { cn } from "../../lib/cn";

/** Free-form multi-entry field — allergies, medications, surgeries, conditions. */
export default function TagInput({ label, placeholder, value = [], onChange, hint, className }) {
  const [draft, setDraft] = useState("");

  const add = () => {
    const v = draft.trim();
    if (!v || value.includes(v)) return;
    onChange?.([...value, v]);
    setDraft("");
  };

  const remove = (tag) => onChange?.(value.filter((t) => t !== tag));

  return (
    <div className={cn("w-full", className)}>
      {label && <label className="mb-2 block text-[13px] font-medium text-fg-soft">{label}</label>}

      <div className="flex gap-2">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          placeholder={placeholder}
          className="h-[52px] flex-1 rounded-[16px] border border-line bg-card px-4 text-[15px] text-fg outline-none transition-all duration-250 placeholder:text-fg-muted/70 hover:border-line-strong focus:border-azure-500/70 focus:ring-4 focus:ring-azure-500/12"
        />
        <button
          type="button"
          onClick={add}
          className="grid h-[52px] w-[52px] shrink-0 place-items-center rounded-[16px] bg-brand-soft text-navy-700 transition-transform hover:scale-[1.03] dark:text-azure-300"
          aria-label="Add"
        >
          <Plus size={18} />
        </button>
      </div>

      {value.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          <AnimatePresence mode="popLayout">
            {value.map((tag) => (
              <motion.span
                key={tag}
                layout
                initial={{ opacity: 0, scale: 0.85 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.85 }}
                className="inline-flex items-center gap-1.5 rounded-full bg-brand-soft py-1.5 pl-3.5 pr-2 text-[13px] font-medium text-navy-700 dark:text-azure-300"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => remove(tag)}
                  className="grid h-4 w-4 place-items-center rounded-full transition-colors hover:bg-navy-700/12"
                  aria-label={`Remove ${tag}`}
                >
                  <X size={11} strokeWidth={2.6} />
                </button>
              </motion.span>
            ))}
          </AnimatePresence>
        </div>
      )}

      {hint && <p className="mt-2 text-[12.5px] text-fg-muted">{hint}</p>}
    </div>
  );
}
