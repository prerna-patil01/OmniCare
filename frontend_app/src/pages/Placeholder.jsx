import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Sparkles } from "lucide-react";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import { cascade, riseIn } from "../lib/motion";

/**
 * Premium empty state used for modules that are next in the build order.
 * Deliberately calm — an OS never apologises loudly for what isn't loaded yet.
 */
export default function Placeholder({ title, description, icon: Icon = Sparkles }) {
  const navigate = useNavigate();

  return (
    <motion.div
      variants={cascade(0.09)}
      initial="initial"
      animate="animate"
      className="mx-auto grid min-h-[62vh] max-w-[560px] place-items-center text-center"
    >
      <div>
        <motion.div variants={riseIn} className="mx-auto mb-8 grid h-20 w-20 place-items-center rounded-[26px] border border-line bg-card shadow-soft">
          <Icon size={30} strokeWidth={1.5} className="text-navy-700 dark:text-azure-300" />
        </motion.div>

        <motion.div variants={riseIn} className="mb-5 flex justify-center">
          <Badge tone="neutral" dot>
            Next in build
          </Badge>
        </motion.div>

        <motion.h1
          variants={riseIn}
          className="font-display text-[34px] font-semibold leading-tight tracking-[-0.03em] text-fg"
        >
          {title}
        </motion.h1>

        <motion.p variants={riseIn} className="mx-auto mt-4 max-w-[440px] text-[15px] leading-relaxed text-fg-muted">
          {description}
        </motion.p>

        <motion.div variants={riseIn} className="mt-9 flex justify-center">
          <Button variant="secondary" size="lg" icon={ArrowLeft} onClick={() => navigate("/dashboard")}>
            Back to Dashboard
          </Button>
        </motion.div>
      </div>
    </motion.div>
  );
}
