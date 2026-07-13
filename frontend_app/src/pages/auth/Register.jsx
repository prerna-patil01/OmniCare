import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import AuthLayout from "../../components/layout/AuthLayout";
import Button from "../../components/ui/Button";
import StepIndicator from "../../components/onboarding/StepIndicator";
import PersonalStep from "../../components/onboarding/steps/PersonalStep";
import MedicalStep from "../../components/onboarding/steps/MedicalStep";
import LifestyleStep from "../../components/onboarding/steps/LifestyleStep";
import ConnectionsStep from "../../components/onboarding/steps/ConnectionsStep";
import { slideStep, riseIn, EASE } from "../../lib/motion";

const STEPS = [
  { label: "Personal", title: "Let's start with you", sub: "The basics your care team always needs first." },
  { label: "Medical", title: "Your medical history", sub: "Everything Omni reasons over before it says a word." },
  { label: "Lifestyle", title: "How you live", sub: "Habits shape risk far more than most people expect." },
  { label: "Connections", title: "Connect your health", sub: "Link the sources that keep your profile alive." },
];

const INITIAL = {
  name: "", dob: "", gender: "", height: "", weight: "", bloodGroup: "", emergencyContact: "",
  allergies: [], currentDiseases: [], pastDiseases: [], surgeries: [], medications: [], familyHistory: [],
  smoking: "", alcohol: "", foodHabits: "", exercise: "", stress: "", hydration: "", sleep: "", occupation: "",
  connections: [],
};

export default function Register() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [dir, setDir] = useState(1);
  const [data, setData] = useState(INITIAL);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const update = (key, value) => {
    setData((d) => ({ ...d, [key]: value }));
    setErrors((e) => ({ ...e, [key]: undefined }));
  };

  /** Only Step 1 is gated — clinical and lifestyle detail is invited, not enforced. */
  const validateStep = () => {
    if (step !== 0) return true;
    const e = {};
    if (!data.name.trim()) e.name = "Required";
    if (!data.dob) e.dob = "Required";
    if (!data.gender) e.gender = "Required";
    if (!data.height || +data.height < 50) e.height = "Enter a valid height in cm";
    if (!data.weight || +data.weight < 10) e.weight = "Enter a valid weight in kg";
    if (!data.bloodGroup) e.bloodGroup = "Required";
    if (!/^[0-9]{10}$/.test(data.emergencyContact)) e.emergencyContact = "Enter a 10-digit number";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const next = () => {
    if (!validateStep()) return;
    if (step === STEPS.length - 1) {
      setSaving(true);
      setTimeout(() => navigate("/dashboard"), 850);
      return;
    }
    setDir(1);
    setStep((s) => s + 1);
  };

  const back = () => {
    if (step === 0) return navigate("/login");
    setDir(-1);
    setStep((s) => s - 1);
  };

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;

  return (
    <AuthLayout asideVariant="register">
      <motion.div initial="initial" animate="animate" className="w-full">
        <motion.div variants={riseIn} className="mb-8">
          <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-fg-muted">
            Step {step + 1} of {STEPS.length}
          </p>
          <h1 className="font-display text-[32px] font-semibold leading-[1.14] tracking-[-0.03em] text-fg sm:text-[36px]">
            {current.title}
          </h1>
          <p className="mt-3 text-[15px] leading-relaxed text-fg-muted">{current.sub}</p>
        </motion.div>

        <motion.div
          variants={riseIn}
          className="rounded-xl2 border border-line bg-card p-7 shadow-lift sm:p-8"
        >
          <StepIndicator steps={STEPS} current={step} />

          <div className="relative overflow-hidden">
            <AnimatePresence mode="wait" custom={dir} initial={false}>
              <motion.div
                key={step}
                custom={dir}
                variants={slideStep}
                initial="initial"
                animate="animate"
                exit="exit"
              >
                {step === 0 && <PersonalStep data={data} update={update} errors={errors} />}
                {step === 1 && <MedicalStep data={data} update={update} />}
                {step === 2 && <LifestyleStep data={data} update={update} />}
                {step === 3 && <ConnectionsStep data={data} update={update} />}
              </motion.div>
            </AnimatePresence>
          </div>

          <div className="mt-9 flex items-center gap-3 border-t border-line pt-7">
            <Button variant="ghost" size="lg" icon={ArrowLeft} onClick={back}>
              Back
            </Button>
            <Button
              size="lg"
              className="flex-1"
              loading={saving}
              onClick={next}
              iconRight={isLast ? Check : ArrowRight}
            >
              {isLast ? "Finish setup" : "Continue"}
            </Button>
          </div>

          {!isLast && step > 0 && (
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2, ease: EASE }}
              onClick={() => {
                setDir(1);
                setStep((s) => s + 1);
              }}
              className="mt-5 w-full text-center text-[13px] font-medium text-fg-muted transition-colors hover:text-fg"
            >
              Skip for now — I'll add this later
            </motion.button>
          )}
        </motion.div>

        <motion.p variants={riseIn} className="mt-8 text-center text-[14px] text-fg-muted">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-semibold text-navy-700 transition-colors hover:text-navy-600 dark:text-azure-300 dark:hover:text-azure-200"
          >
            Sign in
          </Link>
        </motion.p>
      </motion.div>
    </AuthLayout>
  );
}
