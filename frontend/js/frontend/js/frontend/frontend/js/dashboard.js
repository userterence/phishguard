const user = currentUser();
if (!user) location.href = "index.html";

document.getElementById("userName").textContent = user.full_name;
document.getElementById("userRole").textContent = user.role.toUpperCase();

const NAV = {
  admin:   [["overview","Overview"],["records","Detection records"],["reports","Reported sites"],["users","Users"],["awareness","Awareness"]],
  teacher: [["overview","Overview"],["records","Detection records"],["reports","Reported sites"],["awareness","Awareness"]],
  student: [["overview","Overview"],["history","My scan history"],["reports","My reports"],["awareness","Awareness"]]
};

function renderNav() {
  const nav = document.getElementById("nav");
  nav.innerHTML = "";
  NAV[user.role].forEach(([id, label], i) => {
    const b = document.createElement("button");
    b.className = "nav-item" + (i === 0 ? " active" : "");
    b.textContent = label;
    b.onclick = () => showPage(id, label, b);
    nav.appendChild(b);
  });
}

function clearPanels() {
  document.getElementById("adminPanel").hidden = true;
  document.getElementById("reportPanel").hidden = true;
  document.getElementById("awarenessPanel").hidden = true;
  document.getElementById("dataTable").innerHTML = "";
}

async function showPage(id, label, btn) {
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  btn?.classList.add("active");
  document.getElementById("pageTitle").textContent = label;
  clearPanels();
  document.getElementById("cards").innerHTML = "";

  if (id === "overview") await loadOverview();
  if (id === "history") await loadScanHistory();
  if (id === "records") await loadAllRecords();
  if (id === "reports") await loadReports();
  if (id === "users") await loadUsers();
  if (id === "awareness") await loadAwareness();
}

async function loadOverview() {
  let data;
  if (user.role === "admin") data = await api("/api/analytics/admin/overview");
  else if (user.role === "teacher") data = await api("/api/analytics/teacher/overview");
  else data = await api("/api/analytics/student/overview");

  const cards = [
    ["Students", data.total_students],
    ["Teachers", data.total_teachers],
    ["Websites scanned", data.total_scans],
    ["Phishing", data.phishing],
    ["Suspicious", data.suspicious],
    ["Safe", data.safe]
  ].filter(([, v]) => v !== undefined);

  document.getElementById("cards").innerHTML = cards.map(([k, v]) => `
    <div class="stat-card"><span>${k}</span><strong>${v ?? 0}</strong></div>`).join("");

  if (data.recent?.length) {
    renderTable(document.getElementById("dataTable"),
      ["URL","Status","Category","When"],
      data.recent.map(r => [r.url, r.status, r.category || "-", new Date(r.created_at).toLocaleString()]));
  }
  if (user.role !== "student") drawTrendChart();
  showReportForm();
  document.getElementById("awarenessPanel").hidden = false;
  await loadAwareness();
}

function renderTable(table, headers, rows) {
  table.innerHTML = `<thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead>
    <tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody>`;
}

async function loadScanHistory() {
  const rows = await api("/api/scan/history");
  renderTable(document.getElementById("dataTable"), ["URL","Status","Category","Confidence","When"],
    rows.map(r => [r.url, r.status, r.category || "-",
      r.confidence != null ? (r.confidence*100).toFixed(1)+"%" : "n/a",
      new Date(r.created_at).toLocaleString()]));
}

async function loadAllRecords() {
  const rows = await api("/api/analytics/admin/overview");
  renderTable(document.getElementById("dataTable"), ["URL","Status","Category","When"],
    (rows.recent || []).map(r => [r.url, r.status, r.category || "-",
      new Date(r.created_at).toLocaleString()]));
}

async function loadReports() {
  document.getElementById("reportPanel").hidden = false;
  const rows = user.role === "student" ? await api("/api/reports/mine") : await api("/api/reports");
  renderTable(document.getElementById("reportsTable"), ["URL","Category","Status","Reporter"],
    rows.map(r => [r.url, r.category, r.status, r.reporter || r.review_note || "-"]));
}

function showReportForm() {
  document.getElementById("reportPanel").hidden = false;
}

async function loadUsers() {
  const panel = document.getElementById("adminPanel");
  panel.hidden = false;
  const users = await api("/api/admin/users");
  renderTable(document.getElementById("usersTable"), ["Name","Email","Role","Active","Action"],
    users.map(u => [u.full_name, u.email, u.role, u.is_active ? "yes" : "no",
      `<button class="btn btn-sm btn-outline-light" onclick="toggleUser(${u.id}, ${!u.is_active})">
        ${u.is_active ? "Deactivate" : "Activate"}</button>`]));
}

async function toggleUser(id, active) {
  await api(`/api/admin/users/${id}`, { method: "PUT", body: JSON.stringify({ is_active: active }) });
  loadUsers();
}

async function loadAwareness() {
  const items = await api("/api/awareness/materials");
  document.getElementById("awarenessList").innerHTML = items.map(m => `
    <article class="aware-card">
      <h4>${m.title}</h4>
      <span class="tag">${m.category}</span>
      <p>${m.body}</p>
    </article>`).join("");
}

document.getElementById("reportForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/api/reports", { method: "POST", body: JSON.stringify({
    url: document.getElementById("rUrl").value.trim(),
    category: document.getElementById("rCategory").value,
    description: document.getElementById("rDesc").value || null
  })});
  e.target.reset();
  loadReports();
});

document.getElementById("createUserForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/api/admin/users", { method: "POST", body: JSON.stringify({
    full_name: document.getElementById("nuName").value,
    email: document.getElementById("nuEmail").value,
    password: document.getElementById("nuPass").value,
    role: document.getElementById("nuRole").value
  })});
  e.target.reset();
  loadUsers();
});

// Hands the JWT to the extension so it can call the API while you browse
document.getElementById("connectExt").onclick = () => {
  if (!window.chrome?.storage?.local) return alert("Open this dashboard in Chrome with the extension installed.");
  chrome.storage.local.set({ token: token() }, () => alert("Extension connected and signed in."));
};

renderNav();
showPage("overview", "Overview", document.querySelector(".nav-item"));
