document.addEventListener("DOMContentLoaded", () => {
  // Set the graph bar heights from Django's data-height values.
  document.querySelectorAll("[data-height]").forEach((bar) => {
    const height = Number(bar.dataset.height);
    bar.style.height = `${Number.isFinite(height) ? height : 0}%`;
  });

  // Read alarms inserted by Django's json_script template filter.
  const alarmData = document.getElementById("alarm-data");
  if (!alarmData) return;

  let alarms = [];
  try {
    alarms = JSON.parse(alarmData.textContent || "[]");
  } catch {
    return;
  }

  // Create the reminder message if the HTML page doesn't contain one.
  let toast = document.getElementById("alarm-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "alarm-toast";
    toast.className = "alarm-toast";
    document.body.appendChild(toast);
  }

  function ringAlarm() {
    try {
      const AudioContextClass =
        window.AudioContext || window.webkitAudioContext;

      if (!AudioContextClass) return;

      const audio = new AudioContextClass();
      const oscillator = audio.createOscillator();
      const volume = audio.createGain();

      oscillator.frequency.value = 880;
      volume.gain.value = 0.12;

      oscillator.connect(volume);
      volume.connect(audio.destination);
      oscillator.start();

      window.setTimeout(() => {
        oscillator.stop();
        audio.close();
      }, 700);
    } catch {
      // The on-page reminder still appears if audio is unavailable.
    }
  }

  function checkAlarms() {
    const now = new Date();
    const time =
      `${String(now.getHours()).padStart(2, "0")}:` +
      `${String(now.getMinutes()).padStart(2, "0")}`;
    const date =
      `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;

    alarms.forEach((alarm) => {
      if (!alarm.enabled || alarm.time !== time) return;

      const alarmKey = `study-alarm-${alarm.id}-${date}`;
      if (localStorage.getItem(alarmKey)) return;

      localStorage.setItem(alarmKey, "1");
      toast.textContent =
        `⏰ ${alarm.label || "Study reminder"} — time to study!`;
      toast.classList.add("show");

      ringAlarm();

      window.setTimeout(() => {
        toast.classList.remove("show");
      }, 8000);
    });
  }

  checkAlarms();
  window.setInterval(checkAlarms, 10000);
});