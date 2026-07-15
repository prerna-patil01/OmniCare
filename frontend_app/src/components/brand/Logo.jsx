import { cn } from "../../lib/cn";

/**
 * There is no mark. The word IS the logo.
 *
 * Times New Roman, tightly tracked, at scale. The gold AI pill is the
 * only ornament — and it earns its place by carrying meaning, not decoration.
 */
export default function Logo({ size = "md", withPill = true, tagline = false, className }) {
  const sizes = {
    sm: "text-[26px]",
    md: "text-[32px]",
    lg: "text-[42px]",
    xl: "text-[56px]",
  };

  const pillSizes = {
    sm: "px-2 py-0.5 text-[9px]",
    md: "px-2.5 py-1 text-[10px]",
    lg: "px-3 py-1 text-[11px]",
    xl: "px-3.5 py-1.5 text-[13px]",
  };

  return (
    <div className={cn("inline-flex flex-col", className)}>
      <div className="flex items-center gap-3">
        <span className={cn("wordmark text-fg", sizes[size])}>OmniCare</span>
        {withPill && (
          <span
            className={cn(
              "rounded-full border border-gold-500/45 bg-gold-500/10 font-bold tracking-[0.16em] text-gold-600 shadow-gold",
              pillSizes[size]
            )}
          >
            AI
          </span>
        )}
      </div>
      {tagline && (
        <span className="type-eyebrow mt-2.5 text-fg-muted">
          Healthcare Operating System
        </span>
      )}
    </div>
  );
}