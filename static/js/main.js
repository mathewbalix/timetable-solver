document.addEventListener("DOMContentLoaded", () => {
    const statusMsg = document.getElementById("statusMessage");
    loadAllData();

    document.getElementById("generateBtn").addEventListener("click", async () => {
        statusMsg.textContent = "Solving hard constraints & optimizing school preferences...";
        statusMsg.style.color = "#2563eb";
        const res = await fetch("/api/generate", { method: "POST" });
        const data = await res.json();
        statusMsg.textContent = data.message;
        statusMsg.style.color = data.status === "success" ? "#16a34a" : "#dc2626";
        loadAllData();
    });

    document.getElementById("teacherForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("teacherName").value;
        await fetch("/api/teachers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name })
        });
        document.getElementById("teacherName").value = "";
        loadAllData();
    });

    document.getElementById("roomForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("roomName").value;
        await fetch("/api/rooms", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name })
        });
        document.getElementById("roomName").value = "";
        loadAllData();
    });

    document.getElementById("subjectForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
            name: document.getElementById("subjectName").value,
            teacher_id: document.getElementById("subjectTeacher").value,
            hours: parseInt(document.getElementById("subjectHours").value),
            prefer_morning: document.getElementById("preferMorning").checked
        };
        await fetch("/api/subjects", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        document.getElementById("subjectName").value = "";
        loadAllData();
    });

    window.deleteItem = async (table, id) => {
        await fetch(`/api/delete/${table}/${id}`, { method: "DELETE" });
        loadAllData();
    };

    async function loadAllData() {
        const res = await fetch("/api/data");
        const data = await res.json();

        // Populate Teachers
        const tList = document.getElementById("teacherList");
        const tSelect = document.getElementById("subjectTeacher");
        tList.innerHTML = "";
        tSelect.innerHTML = "";
        data.teachers.forEach(t => {
            tList.innerHTML += `<li><span>${t.name}</span><button class="del-btn" onclick="deleteItem('teachers', ${t.id})">X</button></li>`;
            tSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`;
        });

        // Populate Rooms
        const rList = document.getElementById("roomList");
        rList.innerHTML = "";
        data.rooms.forEach(r => {
            rList.innerHTML += `<li><span>${r.name}</span><button class="del-btn" onclick="deleteItem('rooms', ${r.id})">X</button></li>`;
        });

        // Populate Subjects
        const sList = document.getElementById("subjectList");
        sList.innerHTML = "";
        data.subjects.forEach(s => {
            const tag = s.prefer_morning ? "AM" : "Any";
            sList.innerHTML += `<li><span>${s.name} (${s.hours_per_week}h • ${tag})</span><button class="del-btn" onclick="deleteItem('subjects', ${s.id})">X</button></li>`;
        });

        // Populate Timetable Grid
        const tbody = document.getElementById("timetableBody");
        tbody.innerHTML = "";
        const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
        const times = ["8:00 - 9:20", "9:20 - 10:40", "11:00 - 12:20", "12:20 - 1:40", "2:20 - 3:40"];

        for (let p = 1; p <= 5; p++) {
            let row = `<tr><td><strong>Period ${p}</strong><br><small>${times[p - 1]}</small></td>`;
            days.forEach(day => {
                const slots = data.timetable.filter(item => item.day === day && item.period === p);
                if (slots.length > 0) {
                    row += `<td>` + slots.map(slot => `
                        <div class="slot-card" style="margin-bottom:4px;">
                            <div class="slot-subject">${slot.subject_name}</div>
                            <div class="slot-meta">${slot.teacher_name} • ${slot.room_name}</div>
                        </div>
                    `).join("") + `</td>`;
                } else {
                    row += `<td><span class="free-slot">Free</span></td>`;
                }
            });
            row += `</tr>`;
            tbody.innerHTML += row;
        }
    }
});