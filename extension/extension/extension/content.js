// Show an in-page banner on phishing pages
(async () => {
  const res = await chrome.runtime.sendMessage({ type: "scan", url: location.href });
  if (!res || res.status !== "phishing") return;

  const bar = document.createElement("div");
  bar.style.cssText = `
    position:fixed;top:0;left:0;right:0;z-index:2147483647;
    background:#b91c1c;color:#fff;font:600 14px/1.5 system-ui,sans-serif;
    padding:12px 16px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.4)`;
  bar.textContent = "⚠ PhishGuard: this page is flagged as PHISHING. Do not enter your credentials.";
  document.documentElement.appendChild(bar);
})();
