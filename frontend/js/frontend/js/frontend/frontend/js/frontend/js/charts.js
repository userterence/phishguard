let trendChart;

async function drawTrendChart() {
  const data = await api("/api/analytics/trends?days=14");
  const labels = Object.keys(data).sort();
  const mk = (k) => labels.map(d => data[d][k] || 0);

  const ctx = document.getElementById("trendChart");
  if (trendChart) trendChart.destroy();
  trendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Safe",       data: mk("safe"),       borderColor: "#22c55e", tension: .3 },
        { label: "Suspicious", data: mk("suspicious"), borderColor: "#f59e0b", tension: .3 },
        { label: "Phishing",   data: mk("phishing"),   borderColor: "#ef4444", tension: .3 }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#cbd5e1" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" }, beginAtZero: true }
      }
    }
  });
}
