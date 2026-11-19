const API = "[localhost](http://localhost:8000)";

function token() { return localStorage.getItem("pg_token"); }
function currentUser() { return JSON.parse(localStorage.getItem("pg_user") || "null"); }
function logout() { localStorage.removeItem("pg_token"); localStorage.removeItem("pg_user"); location.href = "index.html"; }

async function api(path, options = {}) {
  const headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
  if (token()) headers["Authorization"] = `Bearer ${token()}`;
  const res = await fetch(API + path, { ...options, headers });
  if (res.status === 401) { logout(); throw new Error("Session expired"); }
  if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
  return res.status === 204 ? null : res.json();
}
