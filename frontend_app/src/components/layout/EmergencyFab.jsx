import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Siren, Sparkles } from "lucide-react";
import { EASE } from "../../lib/motion";

/**
 * The two persistent affordances of the OS.
 *
 * Omni (gold)  — always one tap from asking.
 * SOS  (red)   — always one tap from help. Never hidden, never buried.
 *
 * They stack rather than sit side-by-side so the red stays anchored
 * lowest-right: the position your thumb finds without looking.
 */
function Fab({ icon: Icon, label, onClick, tone, delay = 0 }) {
  const [hovered, setHovered] = useState(false);

  const tones = {
    gold: "bg-gold-500 text-white shadow-gold",
    red: "bg-vital-red text-white shadow-lift",
  };
  const pulse = { gold: "bg-gold-500/30", red: "bg-vital-red/35" };

  return (
    <div className="relative flex items-center justify-end">
      {/* label reveals on hover, expands leftward */}
      <AnimatePresence>
        {hovered && (
          <motion.span
            initial={{ opacity: 0, x: 10, scale: 0.94 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 10, scale: 0.94 }}
            transition={{ duration: 0.22, ease: EASE }}
            className="pointer-events-none absolute right-16 whitespace-nowrap rounded-full border border-line bg-card px-4 py-2 text-[14px] font-bold text-fg shadow-lift"
          >
            {label}
          </motion.span>
        )}
      </AnimatePresence>

      <motion.button
        initial={{ opacity: 0, scale: 0.8, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ delay, duration: 0.5, ease: EASE }}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.94 }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        onClick={onClick}
        className={`relative grid h-14 w-14 place-items-center rounded-full ${tones[tone]}`}
        aria-label={label}
      >
        <motion.span
          className={`absolute inset-0 rounded-full ${pulse[tone]}`}
          animate={{ scale: [1, 1.5], opacity: [0.6, 0] }}
          transition={{ duration: tone === "red" ? 1.8 : 2.6, repeat: Infinity, ease: "easeOut" }}
        />
        <Icon size={22} strokeWidth={2} className="relative" />
      </motion.button>
    </div>
  );
}

export default function EmergencyFab() {
  const navigate = useNavigate();

  return (
    <div className="fixed bottom-7 right-7 z-40 flex flex-col gap-3.5">
      <Fab
        icon={Sparkles}
        label="Ask Omni"
        tone="gold"
        delay={0.5}
        onClick={() => navigate("/omni")}
      />
      <Fab
        icon={Siren}
        label="Emergency SOS"
        tone="red"
        delay={0.6}
        onClick={() => navigate("/sos")}
      />
    </div>
  );
}