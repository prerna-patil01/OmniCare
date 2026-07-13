import { useState, forwardRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, Eye, EyeOff } from "lucide-react";
import { cn } from "../../lib/cn";

/** Rounded, generously padded field with an animated focus ring and error state. */
const Input = forwardRef(function Input(
  {
    label,
    hint,
    error,
    icon: Icon,
    suffix,
    type = "text",
    className,
    containerClassName,
    ...rest
  },
  ref
) {
  const [focused, setFocused] = useState(false);
  const [reveal, setReveal] = useState(false);
  const isPassword = type === "password";
  const resolvedType = isPassword && reveal ? "text" : type;

  return (
    <div className={cn("w-full", containerClassName)}>
      {label && (
        <label className="mb-2 block text-[13px] font-medium text-fg-soft">{label}</label>
      )}

      <div
        className={cn(
          "relative flex items-center rounded-[16px] border bg-card transition-all duration-250",
          error
            ? "border-vital-red/60 ring-4 ring-vital-red/10"
            : focused
            ? "border-azure-500/70 ring-4 ring-azure-500/12"
            : "border-line hover:border-line-strong"
        )}
      >
        {Icon && (
          <span className="pl-4 text-fg-muted">
            <Icon size={17} strokeWidth={1.9} />
          </span>
        )}

        <input
          ref={ref}
          type={resolvedType}
          onFocus={(e) => {
            setFocused(true);
            rest.onFocus?.(e);
          }}
          onBlur={(e) => {
            setFocused(false);
            rest.onBlur?.(e);
          }}
          className={cn(
            "h-[52px] w-full bg-transparent px-4 text-[15px] text-fg outline-none",
            "placeholder:text-fg-muted/70",
            Icon && "pl-3",
            className
          )}
          {...rest}
        />

        {isPassword && (
          <button
            type="button"
            onClick={() => setReveal((r) => !r)}
            className="pr-4 text-fg-muted transition-colors hover:text-fg"
            aria-label={reveal ? "Hide password" : "Show password"}
          >
            {reveal ? <EyeOff size={17} /> : <Eye size={17} />}
          </button>
        )}

        {suffix && !isPassword && (
          <span className="whitespace-nowrap pr-4 text-[13px] font-medium text-fg-muted">
            {suffix}
          </span>
        )}
      </div>

      <AnimatePresence mode="wait">
        {error ? (
          <motion.p
            key="error"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            className="mt-2 flex items-center gap-1.5 text-[12.5px] font-medium text-vital-red"
          >
            <AlertCircle size={13} /> {error}
          </motion.p>
        ) : hint ? (
          <p key="hint" className="mt-2 text-[12.5px] text-fg-muted">
            {hint}
          </p>
        ) : null}
      </AnimatePresence>
    </div>
  );
});

export default Input;
