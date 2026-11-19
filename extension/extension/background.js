const API = "[localhost](http://localhost:8000)";

// cache per-tab so we don't re-scan the same URL repeatedly
const cache = {};

async function getToken() {
  const { token } = await chrome.storage.local.get("token");
  return token || null;
}

async function scanUrl(url) {
  if (cache[url]) return cache[url];
  const token = await getToken();
  if (!token) return { status: "unknown", category: "none", reasons: ["Please log in to the dashboard first"], confidence: null };

  try {
    const res = await fetch(`${API}/api/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ url })
    });
    if (!res.ok) throw new Error("scan failed");
    const data = await res.json();
    cache[url] = data;
    await chrome.storage.local.set({ lastScan: data });
    if (data.status === "phishing") notify(data);
    return data;
  } catch (e) {
    return { status: "unknown", category: "none", reasons: ["Backend unreachable"], confidence: null };
  }
}

function notify(data) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/128.png",
    title: "Phishing warning",
    message: `${data.domain || "This site"} looks like a phishing page.`
  });
}

chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (info.status === "complete" && tab.url && tab.url.startsWith("http")) {
    await scanUrl(tab.url);
  }
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "scan") {
    scanUrl(msg.url).then(sendResponse);
    return true;   // keep channel open for async
  }
  if (msg.type === "report") {
    (async () => {
      const token = await getToken();
      const res = await fetch(`${API}/api/reports`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify(msg.payload)
      });
      sendResponse(await res.json());
    })();
    return true;
  }
});
