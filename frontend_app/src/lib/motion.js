/**
 * OmniCare motion language.
 * Every surface enters with a soft, staggered cascade — never a hard cut.
 */

export const EASE = [0.22, 1, 0.36, 1];

export const pageTransition = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.5, ease: EASE } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.28, ease: EASE } },
};

export const cascade = (stagger = 0.07, delay = 0.05) => ({
  initial: {},
  animate: { transition: { staggerChildren: stagger, delayChildren: delay } },
});

export const riseIn = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.55, ease: EASE } },
};

export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.6, ease: EASE } },
};

export const scaleIn = {
  initial: { opacity: 0, scale: 0.96 },
  animate: { opacity: 1, scale: 1, transition: { duration: 0.45, ease: EASE } },
};

export const slideStep = {
  initial: (dir) => ({ opacity: 0, x: dir > 0 ? 40 : -40 }),
  animate: { opacity: 1, x: 0, transition: { duration: 0.45, ease: EASE } },
  exit: (dir) => ({
    opacity: 0,
    x: dir > 0 ? -40 : 40,
    transition: { duration: 0.3, ease: EASE },
  }),
};

export const hoverLift = {
  whileHover: { y: -4, transition: { duration: 0.28, ease: EASE } },
  whileTap: { y: -1, scale: 0.995 },
};
