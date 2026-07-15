/**
 * Ride deep links.
 *
 * No API keys, no partner approval — these open the real Uber/Ola apps
 * with the destination already filled in. On desktop (no app installed)
 * they fall through to the web URL, so the demo never dead-ends.
 */

const isMobile = () => /iPhone|iPad|Android/i.test(navigator.userAgent);

/** @param {{ lat: number, lng: number, destination: string }} d */
export function openUber({ lat, lng, destination }) {
  const deepLink =
    `uber://?action=setPickup&pickup=my_location` +
    `&dropoff[latitude]=${lat}&dropoff[longitude]=${lng}` +
    `&dropoff[nickname]=${encodeURIComponent(destination)}`;

  const webFallback =
    `https://m.uber.com/ul/?action=setPickup&pickup=my_location` +
    `&dropoff[latitude]=${lat}&dropoff[longitude]=${lng}` +
    `&dropoff[nickname]=${encodeURIComponent(destination)}`;

  launch(deepLink, webFallback);
}

export function openOla({ lat, lng }) {
  const deepLink = `olacabs://app/launch?lat=${lat}&lng=${lng}&category=mini`;
  const webFallback = `https://book.olacabs.com/?drop_lat=${lat}&drop_lng=${lng}`;
  launch(deepLink, webFallback);
}

export function openMaps({ lat, lng }) {
  window.open(
    `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`,
    "_blank"
  );
}

/**
 * Try the native app; if nothing handles the scheme the page is still
 * here after ~900ms, so send them to the web version instead.
 */
function launch(deepLink, webFallback) {
  if (!isMobile()) {
    window.open(webFallback, "_blank");
    return;
  }

  const start = Date.now();
  const timer = setTimeout(() => {
    if (Date.now() - start < 1400) window.location.href = webFallback;
  }, 900);

  window.addEventListener("pagehide", () => clearTimeout(timer), { once: true });
  window.location.href = deepLink;
}