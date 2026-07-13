import { motion } from "framer-motion";
import { HeartPulse, Droplets, Moon, Footprints, Sparkles } from "lucide-react";
import StatCard from "../components/ui/StatCard";
import Card, { CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import { cascade, riseIn } from "../lib/motion";
import { DEMO_USER } from "../data/user";

/**
 * Dashboard shell — the full modular Healthcare OS grid lands next.
 * What's here establishes the spacing, rhythm and card language everything else inherits.
 */
export default function Dashboard() {
  return (
    <motion.div variants={cascade(0.07)} initial="initial" animate="animate">
      <motion.header variants={riseIn} className="mb-9 flex flex-wrap items-end justify-between gap-6">
        <div>
          <p className="mb-2.5 text-[11px] font-semibold uppercase tracking-[0.2em] text-fg-muted">
            {new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" })}
          </p>
          <h1 className="font-display text-[38px] font-semibold leading-tight tracking-[-0.03em] text-fg">
            Good to see you, {DEMO_USER.name.split(" ")[0]}.
          </h1>
          <p className="mt-3 text-[15px] text-fg-muted">
            Your vitals are steady. Nothing needs your attention right now.
          </p>
        </div>
        <Badge tone="green" dot>
          All systems normal
        </Badge>
      </motion.header>

      <div className="mb-7 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={HeartPulse} label="Heart Rate" value="72" unit="bpm" delta="+2" tone="red" />
        <StatCard icon={Droplets} label="Hydration" value="2.1" unit="/ 3.0 L" tone="teal" />
        <StatCard icon={Moon} label="Sleep" value="7.4" unit="hrs" delta="+0.6" tone="neutral" />
        <StatCard icon={Footprints} label="Steps" value="6,240" tone="green" />
      </div>

      <Card className="relative overflow-hidden" padding="p-8">
        <div className="absolute -right-16 -top-20 h-64 w-64 rounded-full bg-azure-500/8 blur-3xl" />
        <CardHeader
          icon={Sparkles}
          title="Ask Omni"
          subtitle="Describe how you feel. Omni asks the questions a clinician would."
          action={<Badge tone="neutral">Augmented AI</Badge>}
        />
        <p className="max-w-[620px] text-[15px] leading-relaxed text-fg-soft">
          The full Healthcare OS grid — anatomy preview, risk index, timeline, care services,
          disease intelligence and the rest — builds on this exact card language.
        </p>
        <div className="mt-7">
          <Button size="lg">Open Omni</Button>
        </div>
      </Card>
    </motion.div>
  );
}
