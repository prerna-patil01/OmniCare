import { cn } from "../../lib/cn";

/**
 * OmniCare mark — an interlocking orbit + medical cross.
 * The "orbit" reads as an operating system; the cross grounds it in medicine.
 * Wordmark is Times New Roman by brand rule; nothing else in the app is.
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
          <stop stopColor="#274C99" />
          <stop offset="1" stopColor="#0F2249" />
        </linearGradient>
        <linearGradient id="oc-mark-accent" x1="14" y1="14" x2="34" y2="34" gradientUnits="userSpaceOnUse">
          <stop stopColor="#7A94FF" />
          <stop offset="1" stopColor="#4C6FFF" />
        </linearGradient>
      </defs>

      <rect width="48" height="48" rx="14" fill="url(#oc-mark)" />

      {/* orbit ring */}
      <circle
        cx="24"
        cy="24"
        r="13"
        stroke="url(#oc-mark-accent)"
        strokeWidth="1.6"
        strokeDasharray="3 5"
        strokeLinecap="round"
        opacity="0.85"
      />

      {/* medical cross, geometric */}
      <path
        d="M21.4 13.6a2.6 2.6 0 0 1 5.2 0v5.8h5.8a2.6 2.6 0 0 1 0 5.2h-5.8v5.8a2.6 2.6 0 0 1-5.2 0v-5.8h-5.8a2.6 2.6 0 0 1 0-5.2h5.8v-5.8Z"
        fill="#fff"
        fillOpacity="0.96"
      />

      {/* pulse node */}
      <circle cx="35.4" cy="12.6" r="3" fill="#4C6FFF" />
      <circle cx="35.4" cy="12.6" r="5.6" stroke="#4C6FFF" strokeOpacity="0.35" strokeWidth="1.2" />
    </svg>
  );
}

export default function Logo({ size = 40, showTagline = false, invert = false, className }) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <LogoMark size={size} />
      <div className="leading-none">
        <span
          className={cn(
            "font-brand block text-[26px] tracking-tight",
            invert ? "text-white" : "text-fg"
          )}
        >
          OmniCare
        </span>
        {showTagline && (
          <span
            className={cn(
              "mt-1 block text-[11px] font-medium uppercase tracking-[0.18em]",
              invert ? "text-azure-300" : "text-fg-muted"
            )}
          >
            Healthcare OS
          </span>
        )}
      </div>
    </div>
  );
}
