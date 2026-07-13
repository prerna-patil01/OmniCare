import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Siren } from "lucide-react";
import { EASE } from "../../lib/motion";

/** Always-present SOS. One tap, no confirmation friction, never hidden. */
export default function EmergencyFab() {
  const navigate = useNavigate();

  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.8, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ delay: 0.6, duration: 0.5, ease: EASE }}
      whileHover={{ scale: 1.06 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => navigate("/sos")}
      className="fixed bottom-7 right-7 z-40 grid h-14 w-14 place-items-center rounded-full bg-vital-red text-white shadow-lift"
      aria-label="Emergency SOS"
    >
      <span className="absolute inset-0 animate-ping rounded-full bg-vital-red/35" />
      <Siren size={22} strokeWidth={2} className="relative" />
    </motion.button>
  );
}
