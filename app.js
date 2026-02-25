document.addEventListener("DOMContentLoaded", () => {
  const useLocationBtn = document.getElementById("use-location-btn");
  const statusEl = document.getElementById("location-status");
  const latInput = document.getElementById("latitude");
  const lonInput = document.getElementById("longitude");

  if (!useLocationBtn || !statusEl || !latInput || !lonInput) {
    return;
  }

  if (!("geolocation" in navigator)) {
    statusEl.textContent = "Location detection is not supported on this device.";
    useLocationBtn.disabled = true;
    return;
  }

  useLocationBtn.addEventListener("click", () => {
    statusEl.textContent = "Requesting your location…";
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        latInput.value = latitude.toString();
        lonInput.value = longitude.toString();
        statusEl.textContent = "Location captured. It will be used to find nearby services.";
      },
      (error) => {
        console.error("Geolocation error", error);
        statusEl.textContent =
          "We could not access your location. You can still type an address instead.";
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      }
    );
  });
});

