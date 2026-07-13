import { useState } from "react";
import { motion } from "framer-motion";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

const VARIANTS = {
  primary:
    "bg-navy-700 text-white hover:bg-navy-600 dark:bg-azure-500 dark:hover:bg-azure-400 dark:text-navy-950 shadow-soft",
  secondary:
    "bg-card text-fg border border-line hover:border-line-strong hover:bg-mist-50 dark:hover:bg-navy-800",
  ghost: "bg-transparent text-fg-soft hover:text-fg hover:bg-brand-soft",
  outline:
    "bg-transparent text-navy-700 border border-navy-700/25 hover:bg-navy-700/[0.04] dark:text-azure-300 dark:border-azure-400/30 dark:hover:bg-azure-500/10",
  danger: "bg-vital-red text-white hover:brightness-110 shadow-soft",
  soft: "bg-brand-soft text-navy-700 dark:text-azure-300 hover:brightness-[0.98]",
};

const SIZES = {
  sm: "h-9 px-4 text-[13px] rounded-xl gap-1.5",
  md: "h-11 px-5 text-[14px] rounded-[14px] gap-2",
  lg: "h-[52px] px-6 text-[15px] rounded-2xl gap-2.5",
  xl: "h-14 px-8 text-[16px] rounded-2xl gap-3",
};

/** Primary interactive element. Includes a soft ripple on press. */
export default function Button({
  children,
  variant = "primary",
  size = "md",
  icon: Icon,
  iconRight: IconRight,
  fullWidth = false,
  loading = false,
  disabled = false,
  className,
  onClick,
  type = "button",
  ...rest
}) {
  const [ripples, setRipples] = useState([]);

  const handleClick = (e) => {
    if (disabled || loading) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const id = Date.now();
    setRipples((r) => [...r, { id, x: e.clientX - rect.left, y: e.clientY - rect.top }]);
    setTimeout(() => setRipples((r) => r.filter((it) => it.id !== id)), 620);
    onClick?.(e);
  };

  return (
    <motion.button
      type={type}
      onClick={handleClick}
      disabled={disabled || loading}
      whileHover={disabled ? undefined : { y: -1 }}
      whileTap={disabled ? undefined : { scale: 0.985 }}
      transition={{ duration: 0.2, ease: EASE }}
      className={cn(
        "relative isolate inline-flex select-none items-center justify-center overflow-hidden font-medium",
        "outline-none transition-colors duration-200",
        "focus-visible:ring-2 focus-visible:ring-azure-500/45 focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
        "disabled:cursor-not-allowed disabled:opacity-45",
        VARIANTS[variant],
        SIZES[size],
        fullWidth && "w-full",
        className
      )}
      {...rest}
    >
      {ripples.map((r) => (
        <motion.span
          key={r.id}
          initial={{ opacity: 0.35, scale: 0 }}
          animate={{ opacity: 0, scale: 4 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          style={{ left: r.x, top: r.y }}
          className="pointer-events-none absolute -z-10 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full bg-current"
        />
      ))}

      {loading ? (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : (
        Icon && <Icon size={size === "sm" ? 15 : 17} strokeWidth={2} />
      )}
      {children}
      {IconRight && !loading && <IconRight size={size === "sm" ? 15 : 17} strokeWidth={2} />}
    </motion.button>
  );
}
