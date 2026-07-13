import { Outlet, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import Header from "./Header";
import EmergencyFab from "./EmergencyFab";
import { pageTransition } from "../../lib/motion";

/** The OS shell: sticky chrome, animated page body, persistent SOS. */
export default function AppLayout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-bg">
      <Header />

      <AnimatePresence mode="wait">
        <motion.main
          key={location.pathname}
          variants={pageTransition}
          initial="initial"
          animate="animate"
          exit="exit"
          className="mx-auto max-w-[1560px] px-6 py-10 lg:px-10 lg:py-12"
        >
          <Outlet />
        </motion.main>
      </AnimatePresence>

      <EmergencyFab />
    </div>
  );
}
