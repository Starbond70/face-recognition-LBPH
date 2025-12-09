// Helper to get element
const get = (id) => document.getElementById(id);

// --- Navigation ---
document.querySelectorAll('.nav-links li').forEach(item => {
    item.addEventListener('click', () => {
        // Remove active class from all
        document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
        document.querySelectorAll('section.page').forEach(sec => sec.classList.remove('active'));

        // Add active to clicked
        item.classList.add('active');
        const targetId = item.getAttribute('data-target');
        get(targetId).classList.add('active');

        // Load page specific data
        if (targetId === 'dashboard') loadDashboard();
        if (targetId === 'attendance') startAttendancePolling();
        else stopAttendancePolling();
    });
});

// --- Toast Notification ---
function showToast(message, type = 'success') {
    const toast = get('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// --- Dashboard ---
async function loadDashboard() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();

        get('total-students-count').textContent = data.total_students;
        get('today-attendance-count').textContent = data.today_count;

        const tbody = get('students-table').querySelector('tbody');
        tbody.innerHTML = '';
        data.students.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${s.Id}</td><td>${s.Name}</td>`;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading dashboard:", err);
    }
}

// --- Danger Zone ---
get('btn-clear-data').addEventListener('click', async () => {
    if (!confirm("Are you sure? This will delete EVERYTHING.")) return;

    const password = get('clear-password').value;
    try {
        const res = await fetch('/api/danger/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });
        const data = await res.json();

        if (data.success) {
            showToast(data.message);
            loadDashboard(); // Refresh
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast("Server Error", 'error');
    }
});

// --- Registration ---
get('btn-start-capture').addEventListener('click', async () => {
    const id = get('reg-id').value;
    const name = get('reg-name').value;

    if (!id || !name) {
        showToast("Please enter ID and Name", 'error');
        return;
    }

    try {
        // 1. Check/Add student to CSV
        const res = await fetch('/api/register/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: id, name: name })
        });
        const data = await res.json();

        if (data.success) {
            showToast("Starting Capture...", 'success');

            // 2. Start Video Feed
            const videoImg = get('reg-video-feed');
            get('reg-video-container').querySelector('.placeholder-text').style.display = 'none';
            videoImg.style.display = 'block';
            videoImg.src = `/video_feed/register/${id}/${name}?t=${Date.now()}`;

            // 3. Reset form
            get('reg-id').value = '';
            get('reg-name').value = '';

        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast("Network Error", 'error');
    }
});

// --- Training ---
get('btn-train').addEventListener('click', async () => {
    const btn = get('btn-train');
    const status = get('train-status');

    btn.disabled = true;
    btn.textContent = "Training...";
    status.textContent = "Please wait, processing images...";
    status.style.color = "var(--text-secondary)";

    try {
        const res = await fetch('/api/train', { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            showToast(data.message);
            status.textContent = data.message;
            status.style.color = "var(--accent-green)";
        } else {
            showToast(data.message, 'error');
            status.textContent = "Training Failed: " + data.message;
            status.style.color = "var(--accent-red)";
        }
    } catch (e) {
        showToast("Error triggering training", 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = "Train Model";
    }
});

// --- Attendance ---
let attendanceInterval = null;

get('btn-toggle-camera').addEventListener('click', () => {
    const img = get('att-video-feed');
    const placeholder = get('attendance').querySelector('.placeholder-text');
    const btn = get('btn-toggle-camera');

    if (img.style.display === 'none' || img.src === '') {
        // Start
        img.src = `/video_feed/attendance?t=${Date.now()}`;
        img.style.display = 'block';
        placeholder.style.display = 'none';
        btn.textContent = "Stop Camera";
        btn.classList.replace('secondary', 'danger');

        startAttendancePolling();
    } else {
        // Stop (Just hide image for now, server stream continues until connection drop)
        img.src = "";
        img.style.display = 'none';
        placeholder.style.display = 'block';
        btn.textContent = "Start Camera";
        btn.classList.replace('danger', 'secondary');

        stopAttendancePolling();
    }
});

function startAttendancePolling() {
    if (attendanceInterval) clearInterval(attendanceInterval);
    attendanceInterval = setInterval(updateAttendanceList, 2000);
}

function stopAttendancePolling() {
    if (attendanceInterval) clearInterval(attendanceInterval);
}

async function updateAttendanceList() {
    try {
        const res = await fetch('/api/attendance/current');
        const data = await res.json();

        const list = get('recognized-list');
        list.innerHTML = '';

        if (data.students.length === 0) {
            list.innerHTML = '<li style="justify-content:center; color: var(--text-secondary)">No one recognized yet</li>';
        }

        data.students.forEach(s => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${s.name}</span> <span style="font-size:0.8rem; opacity:0.7">ID: ${s.id}</span>`;
            list.appendChild(li);
        });
    } catch (e) {
        console.error("Polling error", e);
    }
}

get('btn-save-attendance').addEventListener('click', async () => {
    try {
        const res = await fetch('/api/attendance/save', { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            showToast(data.message);
            updateAttendanceList(); // Should be empty now
        } else {
            showToast(data.message, 'warning');
        }
    } catch (e) {
        showToast("Error saving", 'error');
    }
});

get('btn-clear-session').addEventListener('click', async () => {
    await fetch('/api/attendance/clear', { method: 'POST' });
    updateAttendanceList();
    showToast("List cleared");
});

// Initial Load
loadDashboard();
