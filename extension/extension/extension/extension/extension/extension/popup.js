const API = "[localhost](http://localhost:8000)";
const el = (id) => document.getElementById(id);

async function init() {
  const { token } = await chrome.storage.local.get("token");
  el("roleBadge").textContent = token ? "signed in" : "not signed in";

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab?.url?.startsWith("http")) {
    const res = await chrome.runtime.sendMessage({ type: "scan", url: tab.url });
    render(res || {});
  } else {
    render({ status: "unknown", reasons: ["This page cannot be scanned"] });
  }
}

function render(data) {
  const card = el("statusCard");
  card.className = "status-card " + (data.status || "unknown");
  el("statusLabel").textContent = (data.status || "unknown").toUpperCase();
  el("categoryLabel").textContent =
    data.category && data.category !== "none" ? data.category + " phishing" : "";
  el("confidenceLabel").textContent =
    typeof data.confidence === "number" ? `Confidence: ${(data.confidence*100).toFixed(1)}%` : "";
  el("reasonList").innerHTML = (data.reasons || []).map(r => `<li>${r}</li>`).join("");
}

el("refresh").onclick = init;
el("openDashboard").onclick = () => chrome.tabs.create({ url: "[localhost](http://localhost:5500/dashboard.html)" });
el("reportBtn").onclick = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const res = await chrome.runtime.sendMessage({
    type: "report",
    payload: {
      url: tab.url,
      category: el("reportCategory").value,
      description: el("reportDescription").value || null
    }
  });
  el("reportMsg").textContent = res?.id ? "Report submitted — thank you." : "Submission failed.";
};
init();
