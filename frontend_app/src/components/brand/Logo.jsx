import { cn } from "../../lib/cn";

/**
 * OmniCare mark — geometric cross with a gold glow, per the
 * MedClear-inspired header spec. Wordmark: Times New Roman.
 * The AI pill is gold — the one place gold announces itself.
 */
export function LogoMark({ size = 40, className }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      className={cn("shrink-0", className)}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="oc-mark" x1="6" y1="4" x2="42" y2="44" gradientUnits="userSpaceOnUse">
          <stop stopColor="#33486A" />
          <stop offset="1" stopColor="#22314A" />
        </linearGradient>
        <linearGradient id="oc-gold" x1="14" y1="14" x2="34" y2="34" gradientUnits="userSpaceOnUse">
          <stop stopColor="#E8CF9E" />
          <stop offset="1" stopColor="#C6A055" />
        </linearGradient>
        <filter id="oc-glow" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="2.2" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <rect width="48" height="48" rx="14" fill="url(#oc-mark)" />

      <circle
        cx="24" cy="24" r="13"
        stroke="url(#oc-gold)" strokeWidth="1.4"
        strokeDasharray="3 5" strokeLinecap="round" opacity="0.9"
      />

      {/* geometric glowing gold cross */}
      <path
        d="M21.4 13.6a2.6 2.6 0 0 1 5.2 0v5.8h5.8a2.6 2.6 0 0 1 0 5.2h-5.8v5.8a2.6 2.6 0 0 1-5.2 0v-5.8h-5.8a2.6 2.6 0 0 1 0-5.2h5.8v-5.8Z"
        fill="url(#oc-gold)"
        filter="url(#oc-glow)"
      />

      <circle cx="35.4" cy="12.6" r="3" fill="#E8CF9E" />
      <circle cx="35.4" cy="12.6" r="5.6" stroke="#E8CF9E" strokeOpacity="0.4" strokeWidth="1.2" />
    </svg>
  );
}

export default function Logo({ size = 40, showTagline = false, invert = false, withPill = true, className }) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <LogoMark size={size} />
      <div className="flex items-center gap-2.5 leading-none">
        <div>
          <span
            className={cn(
              "font-brand block text-[28px] font-bold tracking-tight",
              invert ? "text-white" : "text-fg"
            )}
          >
            OmniCare
          </span>
          {showTagline && (
            <span
              className={cn(
                "type-eyebrow mt-1 block",
                invert ? "text-gold-300" : "text-fg-muted"
              )}
            >
              Healthcare OS
            </span>
          )}
        </div>
        {withPill && (
          <span className="rounded-full border border-gold-500/40 bg-gold-500/10 px-2.5 py-1 text-[11px] font-bold tracking-[0.12em] text-gold-600 shadow-gold dark:text-gold-400">
            AI
          </span>
        )}
      </div>
    </div>
  );
}