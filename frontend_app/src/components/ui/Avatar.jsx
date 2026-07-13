import { cn } from "../../lib/cn";

export default function Avatar({ name = "User", src, size = 38, className }) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <span
      style={{ width: size, height: size }}
      className={cn(
        "grid shrink-0 place-items-center overflow-hidden rounded-full bg-navy-700 text-[13px] font-semibold text-white ring-2 ring-card dark:bg-azure-500 dark:text-navy-950",
        className
      )}
    >
      {src ? <img src={src} alt={name} className="h-full w-full object-cover" /> : initials}
    </span>
  );
}
