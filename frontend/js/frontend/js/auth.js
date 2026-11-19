document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  try {
    const res = await fetch(API + "/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error("Invalid credentials");
    const data = await res.json();
    localStorage.setItem("pg_token", data.access_token);
    localStorage.setItem("pg_user", JSON.stringify(data.user));
    location.href = "dashboard.html";
  } catch (err) {
    document.getElementById("err").textContent = err.message;
  }
});
