const API_BASE = "http://127.0.0.1:5000";

async function fetchJson(url, opts) {
    opts = opts || {};
    opts.headers = opts.headers || {};
    const token = localStorage.getItem("access_token");
    if (token) opts.headers["Authorization"] = "Bearer " + token;
    const res = await fetch(url, opts);
    return await res.json();
}

async function loadEvents() {
    const json = await fetchJson(`${API_BASE}/events`);
    if (!json.success) { alert("Error loading events"); return; }
    const tbody = document.querySelector("#eventsTable tbody");
    tbody.innerHTML = "";
    json.data.forEach(e => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${e.id}</td><td>${e.title}</td><td>${e.type}</td><td>${e.capacity}</td>
                        <td>${e.registrations}</td>
                        <td>${e.is_cancelled ? '—' : `<button onclick="register(${e.id})">Register</button> <button onclick="attend(${e.id})">Mark Attend</button>`}</td>`;
        tbody.appendChild(tr);
    });
}

async function register(eventId) {
    const token = localStorage.getItem("access_token");
    if (!token) { alert("Login first"); return; }
    const student_id = prompt("Enter your student ID (or leave blank to use your account)");
    const payload = {};
    if (student_id) payload.student_id = parseInt(student_id, 10);
    try {
        const res = await fetch(`${API_BASE}/events/${eventId}/register`, {
            method: "POST",
            headers: {"Content-Type":"application/json", "Authorization":"Bearer " + token},
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (!json.success) { alert("Error: " + json.error); return; }
        alert("Registered");
        loadEvents();
    } catch (err) { alert(err); }
}

async function attend(eventId) {
    const token = localStorage.getItem("access_token");
    const student_id = prompt("Enter your student ID (or leave blank)");
    const payload = { student_id: student_id ? parseInt(student_id,10): undefined, event_id: eventId };
    const res = await fetch(`${API_BASE}/attendance`, {
        method: "POST",
        headers: {"Content-Type":"application/json", "Authorization":"Bearer " + token},
        body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (!json.success) { alert("Error: " + json.error); return; }
    alert("Attendance marked");
    loadEvents();
}

document.addEventListener("DOMContentLoaded", () => {
    loadEvents();
    const form = document.getElementById("feedbackForm");
    if (form) {
        form.addEventListener("submit", async (ev) => {
            ev.preventDefault();
            const token = localStorage.getItem("access_token");
            const payload = {
                student_id: parseInt(document.getElementById("eventId").value, 10), // we reuse field names
                event_id: parseInt(document.getElementById("eventId").value, 10),
                rating: parseInt(document.getElementById("rating").value,10),
                comments: document.getElementById("comments").value
            };
            const res = await fetch(`${API_BASE}/feedback`, {
                method: "POST",
                headers: {"Content-Type":"application/json", "Authorization":"Bearer " + token},
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (!json.success) { alert("Error: " + json.error); return; }
            alert("Feedback sent");
            form.reset();
        });
    }
});
