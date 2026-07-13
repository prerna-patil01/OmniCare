import { motion } from "framer-motion";
import { cn } from "../../lib/cn";
import { riseIn, EASE } from "../../lib/motion";

/**
 * The atomic surface of OmniCare. Large radius, soft elevation, room to breathe.
 * `interactive` adds hover elevation for cards that act as entry points.
 */
export default function Card({
  children,
  className,
  padding = "p-7",
  interactive = false,
  glass = false,
  animate = true,
  ...rest
}) {
  const Comp = animate ? motion.div : "div";
  const motionProps = animate
    ? {
        variants: riseIn,
        ...(interactive
          ? {
              whileHover: { y: -5, transition: { duration: 0.3, ease: EASE } },
              whileTap: { scale: 0.995 },
            }
          : {}),
      }
    : {};

  return (
    <Comp
      className={cn(
        "rounded-card border border-line shadow-soft transition-shadow duration-300",
        glass ? "glass" : "bg-card",
        interactive && "cursor-pointer hover:shadow-lift",
        padding,
        className
      )}
      {...motionProps}
      {...rest}
    >
      {children}
    </Comp>
  );
}

export function CardHeader({ title, subtitle, action, icon: Icon, className }) {
  return (
    <div className={cn("mb-6 flex items-start justify-between gap-4", className)}>
      <div className="flex items-start gap-3.5">
        {Icon && (
          <span className="mt-0.5 grid h-10 w-10 place-items-center rounded-[14px] bg-brand-soft text-navy-700 dark:text-azure-300">
            <Icon size={19} strokeWidth={1.9} />
          </span>
        )}
        <div>
          <h3 className="font-display text-[22px] font-semibold leading-tight tracking-[-0.01em] text-fg">
            {title}
          </h3>
          {subtitle && (
            <p className="mt-1.5 text-[14px] leading-relaxed text-fg-muted">{subtitle}</p>
          )}
        </div>
      </div>
      {action}
    </div>
  );
}
