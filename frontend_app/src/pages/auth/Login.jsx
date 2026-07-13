import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Phone, IdCard, ArrowRight, ArrowLeft, Lock } from "lucide-react";
import AuthLayout from "../../components/layout/AuthLayout";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Checkbox from "../../components/ui/Checkbox";
import { cascade, riseIn, EASE } from "../../lib/motion";
import { cn } from "../../lib/cn";

/** Google mark — inline so we never depend on a remote asset for auth. */
function GoogleIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M23.5 12.27c0-.86-.08-1.68-.22-2.48H12v4.7h6.44a5.5 5.5 0 0 1-2.39 3.6v3h3.86c2.26-2.08 3.56-5.15 3.56-8.82Z" />
      <path fill="#34A853" d="M12 24c3.24 0 5.96-1.08 7.95-2.91l-3.87-3c-1.07.72-2.45 1.15-4.08 1.15-3.13 0-5.79-2.11-6.74-4.96H1.29v3.1A12 12 0 0 0 12 24Z" />
      <path fill="#FBBC05" d="M5.26 14.28a7.2 7.2 0 0 1 0-4.56v-3.1H1.29a12 12 0 0 0 0 10.76l3.97-3.1Z" />
      <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.43-3.42C17.95 1.19 15.24 0 12 0A12 12 0 0 0 1.29 6.62l3.97 3.1C6.21 6.86 8.87 4.75 12 4.75Z" />
    </svg>
  );
}

const METHODS = [
  { id: "google", label: "Continue with Google", icon: GoogleIcon, kind: "oauth" },
  { id: "phone", label: "Continue with Phone Number", icon: Phone, kind: "form" },
  { id: "email", label: "Continue with Email", icon: Mail, kind: "form" },
  { id: "abha", label: "Continue with ABHA ID", icon: IdCard, kind: "form" },
];

export default function Login() {
  const navigate = useNavigate();
  const [method, setMethod] = useState(null); // null = method chooser
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [fields, setFields] = useState({ email: "", password: "", phone: "", abha: "" });
  const [errors, setErrors] = useState({});

  const set = (k) => (e) => {
    setFields((f) => ({ ...f, [k]: e.target.value }));
    setErrors((err) => ({ ...err, [k]: undefined }));
  };

  const validate = () => {
    const e = {};
    if (method === "email") {
      if (!/^\S+@\S+\.\S+$/.test(fields.email)) e.email = "Enter a valid email address";
      if (fields.password.length < 6) e.password = "Minimum 6 characters";
    }
    if (method === "phone" && !/^[0-9]{10}$/.test(fields.phone))
      e.phone = "Enter a valid 10-digit number";
    if (method === "abha" && fields.abha.replace(/\D/g, "").length !== 14)
      e.abha = "ABHA ID must be 14 digits";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const submit = () => {
    if (!validate()) return;
    setLoading(true);
    // Frontend-only: simulate the handshake, then enter the OS.
    setTimeout(() => navigate("/dashboard"), 750);
  };

  return (
    <AuthLayout asideVariant="login">
      <motion.div variants={cascade(0.08, 0.1)} initial="initial" animate="animate">
        {/* ── Heading ──────────────────────────────────────────── */}
        <motion.div variants={riseIn} className="mb-9">
          <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-fg-muted">
            Welcome back
          </p>
          <h1 className="font-display text-[36px] font-semibold leading-[1.12] tracking-[-0.03em] text-fg sm:text-[40px]">
            Sign in to <span className="font-brand font-normal">OmniCare</span>
          </h1>
          <p className="mt-3.5 text-[15px] leading-relaxed text-fg-muted">
            One health identity across doctors, records, pharmacy and care.
          </p>
        </motion.div>

        {/* ── Card ─────────────────────────────────────────────── */}
        <motion.div
          variants={riseIn}
          className="rounded-xl2 border border-line bg-card p-7 shadow-lift sm:p-8"
        >
          <AnimatePresence mode="wait" initial={false}>
            {!method ? (
              <motion.div
                key="chooser"
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -16 }}
                transition={{ duration: 0.3, ease: EASE }}
                className="grid gap-3"
              >
                {METHODS.map((m, i) => (
                  <motion.button
                    key={m.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.05 * i, duration: 0.4, ease: EASE }}
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.99 }}
                    onClick={() =>
                      m.kind === "oauth" ? navigate("/dashboard") : setMethod(m.id)
                    }
                    className={cn(
                      "group flex h-[54px] items-center gap-3.5 rounded-[16px] border border-line bg-card px-5 text-left",
                      "text-[14.5px] font-medium text-fg transition-all duration-250",
                      "hover:border-line-strong hover:shadow-soft"
                    )}
                  >
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-[10px] bg-brand-soft text-navy-700 dark:text-azure-300">
                      <m.icon size={17} strokeWidth={1.9} />
                    </span>
                    {m.label}
                    <ArrowRight
                      size={16}
                      className="ml-auto text-fg-muted transition-transform duration-250 group-hover:translate-x-0.5"
                    />
                  </motion.button>
                ))}
              </motion.div>
            ) : (
              <motion.div
                key={method}
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 16 }}
                transition={{ duration: 0.3, ease: EASE }}
              >
                <button
                  onClick={() => {
                    setMethod(null);
                    setErrors({});
                  }}
                  className="mb-6 inline-flex items-center gap-1.5 text-[13px] font-medium text-fg-muted transition-colors hover:text-fg"
                >
                  <ArrowLeft size={14} /> All sign-in options
                </button>

                <div className="grid gap-5">
                  {method === "email" && (
                    <>
                      <Input
                        label="Email address"
                        type="email"
                        icon={Mail}
                        placeholder="you@example.com"
                        value={fields.email}
                        onChange={set("email")}
                        error={errors.email}
                      />
                      <Input
                        label="Password"
                        type="password"
                        icon={Lock}
                        placeholder="Enter your password"
                        value={fields.password}
                        onChange={set("password")}
                        error={errors.password}
                      />
                    </>
                  )}

                  {method === "phone" && (
                    <Input
                      label="Phone number"
                      icon={Phone}
                      inputMode="numeric"
                      maxLength={10}
                      placeholder="98765 43210"
                      value={fields.phone}
                      onChange={set("phone")}
                      error={errors.phone}
                      hint="We'll send a one-time password to this number."
                    />
                  )}

                  {method === "abha" && (
                    <Input
                      label="ABHA ID"
                      icon={IdCard}
                      placeholder="12-3456-7890-1234"
                      value={fields.abha}
                      onChange={set("abha")}
                      error={errors.abha}
                      hint="Your Ayushman Bharat Health Account number."
                    />
                  )}

                  <div className="flex items-center justify-between">
                    <Checkbox checked={remember} onChange={setRemember} label="Remember me" />
                    <Link
                      to="/login"
                      className="text-[13px] font-medium text-navy-700 transition-colors hover:text-navy-600 dark:text-azure-300 dark:hover:text-azure-200"
                    >
                      Forgot password?
                    </Link>
                  </div>

                  <Button size="lg" fullWidth loading={loading} onClick={submit} iconRight={ArrowRight}>
                    {method === "phone" ? "Send OTP" : "Sign in"}
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="mt-7 border-t border-line pt-6 text-center">
            <p className="text-[14px] text-fg-muted">
              New to OmniCare?{" "}
              <Link
                to="/register"
                className="font-semibold text-navy-700 transition-colors hover:text-navy-600 dark:text-azure-300 dark:hover:text-azure-200"
              >
                Create an account
              </Link>
            </p>
          </div>
        </motion.div>

        {/* ── Legal ────────────────────────────────────────────── */}
        <motion.p variants={riseIn} className="mt-8 text-center text-[12.5px] leading-relaxed text-fg-muted">
          By continuing you agree to OmniCare's{" "}
          <a href="#terms" className="font-medium text-fg-soft underline-offset-4 hover:underline">
            Terms &amp; Conditions
          </a>{" "}
          and{" "}
          <a href="#privacy" className="font-medium text-fg-soft underline-offset-4 hover:underline">
            Privacy Policy
          </a>
          .
        </motion.p>
      </motion.div>
    </AuthLayout>
  );
}
