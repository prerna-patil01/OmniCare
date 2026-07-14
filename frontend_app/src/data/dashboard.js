/** Local demo state for the Innovation Grid. Frontend-only. */

export const VITALS = [
  { key: "hr",    label: "Heart Rate", value: "72",  unit: "bpm", delta: "+2",   tone: "red" },
  { key: "hrv",   label: "HRV",        value: "52",  unit: "ms",  delta: "−4",   tone: "amber" },
  { key: "spo2",  label: "SpO₂",       value: "98",  unit: "%",   delta: "—",    tone: "teal" },
  { key: "sleep", label: "Sleep",      value: "6.4", unit: "hrs", delta: "−1.1", tone: "amber" },
];

export const HABITS = [
  { label: "Hydration",  value: "1.2",   unit: "/ 3.0 L", pct: 40, tone: "red",   flag: "Below baseline" },
  { label: "Steps",      value: "6,240", unit: "/ 10k",   pct: 62, tone: "green", flag: null },
  { label: "Sleep debt", value: "4.2",   unit: "hrs",     pct: 78, tone: "amber", flag: "3 nights short" },
];

export const OMNI_THREAD = [
  { from: "user", text: "I've had a dull ache in my upper right abdomen since Sunday." },
  { from: "omni", text: "Does it worsen after eating fatty food, or radiate toward your right shoulder blade?" },
  { from: "user", text: "Yes — worse after dinner. And it does go up toward my shoulder." },
  { from: "omni", text: "Noted. Any nausea, fever, or change in stool colour in the last 72 hours?" },
];

export const FULFILLMENT = {
  pharmacy: [
    { name: "Pantoprazole 40mg", qty: "×14", status: "ROUTE", eta: "Today, 7:40 PM" },
    { name: "ORS Sachets",       qty: "×6",  status: "ROUTE", eta: "Today, 7:40 PM" },
  ],
  transit: {
    provider: "Uber",
    status: "BOOKED",
    eta: "6 min",
    destination: "Apollo Hospitals, Jubilee Hills",
  },
  care: [
    { role: "Home Nurse",  name: "Sr. Kavitha R.", rate: "₹340/hr", available: "Now" },
    { role: "ASHA Worker", name: "Lakshmi D.",     rate: "₹180/hr", available: "Tomorrow" },
  ],
};

export const ECOSYSTEM = {
  hospital: { name: "Apollo Hospitals", distance: "2.4 km", erLoad: 68, consent: "Signed" },
  epidemic: { region: "Hyderabad · Central", index: 4.2, trend: "+0.8", driver: "Viral fever" },
};