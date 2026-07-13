import {
  LayoutGrid, Stethoscope, HeartHandshake, CalendarDays, FolderHeart,
  FlaskConical, Pill, Sparkles, Activity, Radar, ShieldCheck, Car,
} from "lucide-react";

/** Primary OS navigation — care flow first, intelligence after. */
export const PRIMARY_NAV = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutGrid },
  { label: "Find Doctors", to: "/doctors", icon: Stethoscope },
  { label: "Care Services", to: "/care", icon: HeartHandshake },
  { label: "Appointments", to: "/appointments", icon: CalendarDays },
  { label: "Rides", to: "/rides", icon: Car },
  { label: "Health Records", to: "/records", icon: FolderHeart },
  { label: "Reports", to: "/reports", icon: FlaskConical },
  { label: "Pharmacy", to: "/pharmacy", icon: Pill },
  { label: "Ask Omni", to: "/omni", icon: Sparkles },
  { label: "Health Insights", to: "/insights", icon: Activity },
  { label: "Disease Intelligence", to: "/intelligence", icon: Radar },
  { label: "Insurance", to: "/insurance", icon: ShieldCheck },
];