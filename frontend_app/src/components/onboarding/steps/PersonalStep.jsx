import { useMemo } from "react";
import { User, Mail, Lock, Calendar, Ruler, Weight, Phone } from "lucide-react";
import Input from "../../ui/Input";
import Select from "../../ui/Select";
import Badge from "../../ui/Badge";

const GENDERS = ["Female", "Male", "Other", "Prefer not to say"];
const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

/** BMI is derived, never asked. Category thresholds follow WHO adult ranges. */
function bmiCategory(bmi) {
  if (bmi < 18.5) return { label: "Underweight", tone: "amber" };
  if (bmi < 25) return { label: "Healthy range", tone: "green" };
  if (bmi < 30) return { label: "Overweight", tone: "amber" };
  return { label: "Obese", tone: "red" };
}

export default function PersonalStep({ data, update, errors }) {
  const bmi = useMemo(() => {
    const h = parseFloat(data.height);
    const w = parseFloat(data.weight);
    if (!h || !w || h < 50) return null;
    return +(w / (h / 100) ** 2).toFixed(1);
  }, [data.height, data.weight]);

  const cat = bmi ? bmiCategory(bmi) : null;

  return (
    <div className="grid gap-6">
      <Input
        label="Full name"
        icon={User}
        placeholder="Enter your full name"
        value={data.name}
        onChange={(e) => update("name", e.target.value)}
        error={errors.name}
      />

      <div className="grid gap-6 sm:grid-cols-2">
        <Input
          label="Email address"
          type="email"
          icon={Mail}
          value={data.email}
          onChange={(e) => update("email", e.target.value)}
          error={errors.email}
        />
        <Input
          label="Password"
          type="password"
          icon={Lock}
          value={data.password}
          onChange={(e) => update("password", e.target.value)}
          error={errors.password}
          hint="At least 8 characters."
        />
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <Input
          label="Date of birth"
          type="date"
          icon={Calendar}
          value={data.dob}
          onChange={(e) => update("dob", e.target.value)}
          error={errors.dob}
        />
        <Select
          label="Gender"
          options={GENDERS}
          value={data.gender}
          onChange={(v) => update("gender", v)}
          placeholder="Select gender"
          error={errors.gender}
        />
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <Input
          label="Height"
          icon={Ruler}
          inputMode="decimal"
          suffix="cm"
          placeholder="165"
          value={data.height}
          onChange={(e) => update("height", e.target.value)}
          error={errors.height}
        />
        <Input
          label="Weight"
          icon={Weight}
          inputMode="decimal"
          suffix="kg"
          placeholder="56"
          value={data.weight}
          onChange={(e) => update("weight", e.target.value)}
          error={errors.weight}
        />
      </div>

      {/* Derived BMI card */}
      <div className="flex items-center justify-between rounded-lg2 border border-line bg-brand-soft/60 px-5 py-4">
        <div>
          <p className="text-[11.5px] font-semibold uppercase tracking-[0.1em] text-fg-muted">
            Body Mass Index
          </p>
          <p className="mt-1 font-display text-[26px] font-semibold tracking-[-0.02em] text-fg">
            {bmi ?? "—"}
          </p>
        </div>
        {cat ? (
          <Badge tone={cat.tone} dot>
            {cat.label}
          </Badge>
        ) : (
          <p className="max-w-[180px] text-right text-[12.5px] leading-relaxed text-fg-muted">
            Calculated automatically from height and weight.
          </p>
        )}
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <Select
          label="Blood group"
          options={BLOOD_GROUPS}
          value={data.bloodGroup}
          onChange={(v) => update("bloodGroup", v)}
          placeholder="Select"
          error={errors.bloodGroup}
        />
        <Input
          label="Emergency contact"
          icon={Phone}
          inputMode="numeric"
          maxLength={10}
          placeholder="98765 43210"
          value={data.emergencyContact}
          onChange={(e) => update("emergencyContact", e.target.value)}
          error={errors.emergencyContact}
          hint="Reached instantly when you trigger SOS."
        />
      </div>
    </div>
  );
}
