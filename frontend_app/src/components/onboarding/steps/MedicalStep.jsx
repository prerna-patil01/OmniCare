import TagInput from "../../ui/TagInput";

/**
 * Everything here is optional but high-value: it is the context Omni reasons over.
 * Free-form tags rather than dropdowns — real medical histories don't fit enums.
 */
export default function MedicalStep({ data, update }) {
  return (
    <div className="grid gap-6">
      <TagInput
        label="Allergies"
        placeholder="e.g. Penicillin, Peanuts, Dust"
        value={data.allergies}
        onChange={(v) => update("allergies", v)}
        hint="Press Enter to add each one."
      />

      <TagInput
        label="Current conditions"
        placeholder="e.g. Asthma, Hypertension, PCOS"
        value={data.currentDiseases}
        onChange={(v) => update("currentDiseases", v)}
      />

      <TagInput
        label="Past medical history"
        placeholder="e.g. Dengue (2021), Typhoid (2018)"
        value={data.pastDiseases}
        onChange={(v) => update("pastDiseases", v)}
      />

      <TagInput
        label="Previous surgeries"
        placeholder="e.g. Appendectomy (2019)"
        value={data.surgeries}
        onChange={(v) => update("surgeries", v)}
      />

      <TagInput
        label="Current medications"
        placeholder="e.g. Metformin 500mg — twice daily"
        value={data.medications}
        onChange={(v) => update("medications", v)}
      />

      <TagInput
        label="Family history"
        placeholder="e.g. Diabetes (father), Cardiac (grandmother)"
        value={data.familyHistory}
        onChange={(v) => update("familyHistory", v)}
        hint="Hereditary risk meaningfully sharpens early detection."
      />
    </div>
  );
}
