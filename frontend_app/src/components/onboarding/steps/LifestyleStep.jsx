import ChipGroup from "../../ui/ChipGroup";
import Input from "../../ui/Input";
import Select from "../../ui/Select";
import { Droplets, Moon, Briefcase } from "lucide-react";

const SLEEP = [
  { value: "<5", label: "Less than 5 hours" },
  { value: "5-6", label: "5 – 6 hours" },
  { value: "6-7", label: "6 – 7 hours" },
  { value: "7-8", label: "7 – 8 hours" },
  { value: ">8", label: "More than 8 hours" },
];

export default function LifestyleStep({ data, update }) {
  return (
    <div className="grid gap-7">
      <ChipGroup
        label="Smoking"
        options={["Never", "Occasionally", "Regularly", "Quit"]}
        value={data.smoking}
        onChange={(v) => update("smoking", v)}
      />

      <ChipGroup
        label="Alcohol"
        options={["Never", "Socially", "Weekly", "Daily"]}
        value={data.alcohol}
        onChange={(v) => update("alcohol", v)}
      />

      <ChipGroup
        label="Food habits"
        options={["Vegetarian", "Non-vegetarian", "Vegan", "Eggetarian"]}
        value={data.foodHabits}
        onChange={(v) => update("foodHabits", v)}
      />

      <ChipGroup
        label="Exercise"
        options={["Sedentary", "1–2 × week", "3–4 × week", "Daily"]}
        value={data.exercise}
        onChange={(v) => update("exercise", v)}
      />

      <ChipGroup
        label="Stress level"
        options={["Low", "Moderate", "High", "Severe"]}
        value={data.stress}
        onChange={(v) => update("stress", v)}
      />

      <div className="grid gap-6 sm:grid-cols-2">
        <Input
          label="Daily water intake"
          icon={Droplets}
          inputMode="decimal"
          suffix="litres"
          placeholder="2.5"
          value={data.hydration}
          onChange={(e) => update("hydration", e.target.value)}
        />
        <Select
          label="Average sleep"
          icon={Moon}
          options={SLEEP}
          value={data.sleep}
          onChange={(v) => update("sleep", v)}
          placeholder="Select"
        />
      </div>

      <Input
        label="Occupation"
        icon={Briefcase}
        placeholder="e.g. Student, Software Engineer"
        value={data.occupation}
        onChange={(e) => update("occupation", e.target.value)}
        hint="Sedentary and high-exposure roles change baseline risk."
      />
    </div>
  );
}
