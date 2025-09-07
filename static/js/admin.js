// admin.js
const API_BASE = "http://127.0.0.1:5000";

async function fetchJson(url, opts) {
    opts = opts || {};
    opts.headers = opts.headers || {};
    const token = localStorage.getItem("access_token");
    if (token) opts.headers["Authorization"] = "Bearer " + token;
    const res = await fetch(url, opts);
    const json = await res.json();
    return json;
}

async function loadEvents() {
    const json = await fetchJson(`${API_BASE}/events`);
    if (!json.success) {
        alert("Error: " + json.error);
        return;
    }
    const tbody = document.querySelector("#eventsTable tbody");
    tbody.innerHTML = "";
    json.data.forEach(e => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${e.id}</td><td>${e.title}</td><td>${e.type}</td><td>${e.capacity}</td>
                        <td>${e.registrations}</td><td>${e.attendance_count}</td>
                        <td>
                          ${e.is_cancelled ? "Cancelled" : `<button onclick="cancelEvent(${e.id})">Cancel</button>`}
                        </td>`;
        tbody.appendChild(tr);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const btnCreate = document.getElementById("btnCreateEvent");
    if (btnCreate) {
        btnCreate.addEventListener("click", async () => {
            const title = document.getElementById("evTitle").value;
            const type = document.getElementById("evType").value;
            const cap = parseInt(document.getElementById("evCap").value || 50, 10);
            const token = localStorage.getItem("access_token");
            if (!token) { alert("Please login as admin"); return; }
            const res = await fetch(`${API_BASE}/events`, {
                method: "POST",
                headers: {"Content-Type":"application/json", "Authorization":"Bearer " + token},
                body: JSON.stringify({title, type, capacity: cap})
            });
            const json = await res.json();
            if (!json.success) { alert("Error: " + json.error); return; }
            alert("Created");
            loadEvents();
        });
    }

    loadEvents();
});

async function cancelEvent(id) {
    if (!confirm("Cancel event?")) return;
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${API_BASE}/events/${id}/cancel`, {
        method: "POST",
        headers: {"Authorization":"Bearer " + token}
    });
    const json = await res.json();
    if (!json.success) { alert("Error: " + json.error); return; }
    alert("Cancelled");
    loadEvents();
}

// Reports
async function getEventPopularity() {
    const json = await fetchJson(`${API_BASE}/reports/event_popularity?college_id=1`);
    displayReport("Event Popularity", json.data, ["event_id","title","type","registrations"]);
}
async function getTopActiveStudents() {
    const json = await fetchJson(`${API_BASE}/reports/top_active_students?college_id=1&limit=5`);
    displayReport("Top Active Students", json.data, ["student_id","name","events_attended"]);
}
async function getAverageFeedback() {
    const json = await fetchJson(`${API_BASE}/reports/average_feedback?college_id=1`);
    displayReport("Average Feedback", json.data, ["event_id","title","average_rating","feedback_count"]);
}
function displayReport(title, data, fields) {
    let html = `<h3>${title}</h3><table><tr>${fields.map(f=>`<th>${f}</th>`).join("")}</tr>`;
    data.forEach(row => {
        html += "<tr>" + fields.map(f => `<td>${row[f] ?? ""}</td>`).join("") + "</tr>";
    });
    html += "</table>";
    document.getElementById("report").innerHTML = html;
}
