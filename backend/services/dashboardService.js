import { getProfile } from "./profile";
import { getVitals } from "./vitals";
import { getSignals } from "./intelligence";

export async function getDashboard() {
  const [profile, vitals, intelligence] = await Promise.all([
    getProfile(),
    getVitals(),
    getSignals(),
  ]);

  return {
    profile,
    vitals,
    intelligence,
  };
}