import { motion } from "framer-motion";
import AuthAside from "../auth/AuthAside";
import ThemeToggle from "../ui/ThemeToggle";
import { pageTransition } from "../../lib/motion";

/**
 * Split canvas used by Login and Registration.
 * Left: the brand world. Right: the task. Never the other way round.
 */
export default function AuthLayout({ children, asideVariant = "login" }) {
  return (
    <div className="flex min-h-screen bg-bg">
      <AuthAside variant={asideVariant} />

      <main className="relative flex flex-1 items-center justify-center px-6 py-12 sm:px-10 lg:px-16">
        <div className="absolute right-6 top-6 sm:right-10 sm:top-8">
          <ThemeToggle />
        </div>

        <motion.div
          variants={pageTransition}
          initial="initial"
          animate="animate"
          className="w-full max-w-[460px]"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
