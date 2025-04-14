// --- FETCH WEATHER INFO USING OPENWEATHERMAP API ---
const apiKey = "65a2b4e2a781eab6d8d2c63f22d5302a";
const city = "Srinagar";

async function getWeather() {
  try {
    const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`);
    const data = await res.json();
    document.querySelector(".weather-city").innerText = `📍 ${data.name}`;
    document.querySelector(".weather-desc").innerText = `☁️ ${data.weather[0].description}`;
    document.querySelector(".weather-temp").innerText = `🌡️ Temperature: ${data.main.temp}°C`;
    document.querySelector(".weather-humidity").innerText = `💧 Humidity: ${data.main.humidity}%`;
  } catch {
    document.getElementById("weather-info").innerText = "⚠️ Failed to fetch weather.";
  }
}

getWeather();

// --- TOGGLE SIDEBAR VISIBILITY ---
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const content = document.getElementById('main-content');
  const isHidden = sidebar.classList.toggle('hidden');
  content.classList.toggle('full', isHidden);
}
// --- DARK MODE TOGGLE HANDLER ---
const toggle = document.getElementById("darkToggle");
const currentMode = localStorage.getItem("mode");

if (currentMode === "dark") {
  document.body.classList.add("dark");
  toggle.checked = true;
}

toggle.addEventListener("change", () => {
  if (toggle.checked) {
    document.body.classList.add("dark");
    localStorage.setItem("mode", "dark");
  } else {
    document.body.classList.remove("dark");
    localStorage.setItem("mode", "light");
  }
});

