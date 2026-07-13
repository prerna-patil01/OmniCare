import { cn } from "../../lib/cn";

const TONES = {
  neutral: "bg-brand-soft text-navy-700 dark:text-azure-300",
  green: "bg-vital-green/10 text-vital-green",
  amber: "bg-vital-amber/12 text-vital-amber",
  red: "bg-vital-red/10 text-vital-red",
  teal: "bg-vital-teal/10 text-vital-teal",
  outline: "border border-line text-fg-muted",
};

export default function Badge({ children, tone = "neutral", dot = false, className }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11.5px] font-semibold uppercase tracking-[0.06em]",
        TONES[tone],
        className
      )}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
}
