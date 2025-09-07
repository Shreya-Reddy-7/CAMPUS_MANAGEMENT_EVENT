const API_BASE = "http://127.0.0.1:5000";

function saveToken(t) {
    localStorage.setItem("access_token", t);
}

function getToken() {
    return localStorage.getItem("access_token");
}

function removeToken() {
    localStorage.removeItem("access_token");
}

async function login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({email, password})
    });
    const json = await res.json();
    return json;
}

document.addEventListener("DOMContentLoaded", () => {
    const btnLogin = document.getElementById("btnLogin");
    if (btnLogin) {
        btnLogin.addEventListener("click", async () => {
            const email = document.getElementById("email").value;
            const pwd = document.getElementById("password").value;
            const resp = await login(email, pwd);
            if (!resp.success) {
                alert("Login failed: " + resp.error);
                return;
            }
            saveToken(resp.data.access_token);
            alert("Login ok. Role: " + resp.data.role);
        });
    }

    const btnLogout = document.getElementById("btnLogout");
    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            removeToken();
            alert("Logged out");
            window.location.href = "/";
        });
    }
});
