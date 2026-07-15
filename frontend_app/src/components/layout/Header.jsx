import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, Menu, X, Siren } from "lucide-react";
import Logo from "../brand/Logo";
import UniversalSearch from "./UniversalSearch";
import ProfileDropdown from "./ProfileDropdown";
import ThemeToggle from "../ui/ThemeToggle";
import { PRIMARY_NAV } from "../../data/nav";
import { DEMO_USER } from "../../data/user";
import { cn } from "../../lib/cn";
import { EASE } from "../../lib/motion";

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const session = `${DEMO_USER.name.split(" ")[0].toUpperCase()} // PATIENT`;

  return (
    <header className="sticky top-0 z-50 border-b border-line glass">
      <div className="mx-auto flex h-[78px] max-w-[1560px] items-center gap-6 px-6 lg:px-10">
        <button onClick={() => navigate("/dashboard")} className="shrink-0 outline-none">
          <Logo size="sm" />
        </button>

        <div className="hidden max-w-[400px] flex-1 xl:block">
          <UniversalSearch />
        </div>

        <div className="ml-auto flex items-center gap-2.5">
          <span className="mr-1 hidden rounded-full border border-line bg-surface/70 px-3.5 py-1.5 text-[11px] font-bold tracking-[0.16em] text-fg-muted lg:block">
            {session}
          </span>

          <button
            onClick={() => navigate("/sos")}
            className="hidden items-center gap-2 rounded-full bg-vital-red/10 px-4 py-2 text-[14px] font-bold text-vital-red transition-colors hover:bg-vital-red/16 sm:flex"
          >
            <Siren size={15} strokeWidth={2.2} />
            SOS
          </button>

          <button className="relative grid h-10 w-10 place-items-center rounded-full border border-line bg-card text-fg-soft transition-colors hover:text-fg">
            <Bell size={16} strokeWidth={1.9} />
            <span className="absolute right-2.5 top-2.5 h-1.5 w-1.5 rounded-full bg-vital-red ring-2 ring-card" />
          </button>

          <ThemeToggle />
          <ProfileDropdown />

          <button
            onClick={() => setMobileOpen((o) => !o)}
            className="grid h-10 w-10 place-items-center rounded-full border border-line bg-card text-fg-soft lg:hidden"
            aria-label="Menu"
          >
            {mobileOpen ? <X size={17} /> : <Menu size={17} />}
          </button>
        </div>
      </div>

      <nav className="no-scrollbar hidden overflow-x-auto border-t border-line lg:block">
        <ul className="mx-auto flex max-w-[1560px] items-center gap-1 px-6 lg:px-10">
          {PRIMARY_NAV.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "relative flex items-center gap-2 whitespace-nowrap px-3.5 py-3.5 text-[15px] font-bold transition-colors",
                    isActive ? "text-fg" : "text-fg-muted hover:text-fg-soft"
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon size={15} strokeWidth={1.9} />
                    {item.label}
                    {isActive && (
                      <motion.span
                        layoutId="nav-underline"
                        transition={{ duration: 0.35, ease: EASE }}
                        className="absolute inset-x-2 -bottom-px h-[2px] rounded-full bg-ink-700"
                      />
                    )}
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.32, ease: EASE }}
            className="overflow-hidden border-t border-line bg-card lg:hidden"
          >
            <div className="p-5">
              <UniversalSearch className="mb-4" />
              <ul className="grid gap-1">
                {PRIMARY_NAV.map((item) => (
                  <li key={item.to}>
                    <NavLink
                      to={item.to}
                      onClick={() => setMobileOpen(false)}
                      className={({ isActive }) =>
                        cn(
                          "flex items-center gap-3 rounded-[14px] px-3.5 py-3 text-[16px] font-bold transition-colors",
                          isActive
                            ? "bg-brand-soft text-ink-700"
                            : "text-fg-soft hover:bg-surface"
                        )
                      }
                    >
                      <item.icon size={16} strokeWidth={1.9} />
                      {item.label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}