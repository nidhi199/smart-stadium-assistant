import Chart from 'chart.js/auto';

const API_BASE = 'http://localhost:5000/api';

// Tab Switching Logic
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        
        const targetId = e.target.getAttribute('data-target');
        e.target.classList.add('active');
        document.getElementById(targetId).classList.add('active');
        
        if (targetId === 'dashboard-panel') {
            loadDashboard();
        }
    });
});

// Chat Logic
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    chatInput.value = '';
    
    // Disable input while waiting
    chatInput.disabled = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();
        appendMessage(data.reply, 'bot');
    } catch (error) {
        console.error(error);
        appendMessage('Error: Could not connect to the server.', 'bot');
    } finally {
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Dashboard Logic
let zoneChartInstance = null;
let gateChartInstance = null;

async function loadDashboard() {
    try {
        // Load Insight
        const insightRes = await fetch(`${API_BASE}/insight`);
        const insightData = await insightRes.json();
        document.getElementById('insight-text').textContent = insightData.insight;

        // Load Data
        const dashRes = await fetch(`${API_BASE}/dashboard`);
        const data = await dashRes.json();

        renderCharts(data);
        renderIncidents(data.incidents);

    } catch (error) {
        console.error("Dashboard error:", error);
        document.getElementById('insight-text').textContent = "Failed to load insights. Check server connection.";
    }
}

function renderCharts(data) {
    const zoneLabels = data.zones.map(z => z.zone_name);
    const currentCap = data.zones.map(z => z.current_capacity);
    const maxCap = data.zones.map(z => z.max_capacity);

    const gateLabels = data.gate_flow.map(g => g.gate_name);
    const gateFlow = data.gate_flow.map(g => g.entry_rate_per_min);

    // Zone Chart
    const ctxZone = document.getElementById('zone-chart').getContext('2d');
    if (zoneChartInstance) zoneChartInstance.destroy();
    
    zoneChartInstance = new Chart(ctxZone, {
        type: 'bar',
        data: {
            labels: zoneLabels,
            datasets: [{
                label: 'Current Capacity',
                data: currentCap,
                backgroundColor: '#1d3557'
            }, {
                label: 'Max Capacity',
                data: maxCap,
                backgroundColor: '#e5e7eb'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Gate Flow Chart
    const ctxGate = document.getElementById('gate-chart').getContext('2d');
    if (gateChartInstance) gateChartInstance.destroy();
    
    gateChartInstance = new Chart(ctxGate, {
        type: 'line',
        data: {
            labels: gateLabels,
            datasets: [{
                label: 'Entry Rate (per min)',
                data: gateFlow,
                borderColor: '#0a8a3c',
                backgroundColor: 'rgba(10, 138, 60, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderIncidents(incidents) {
    const list = document.getElementById('incidents-list');
    list.innerHTML = '';
    
    if (!incidents || incidents.length === 0) {
        list.innerHTML = '<li>No active incidents.</li>';
        return;
    }

    incidents.forEach(inc => {
        const li = document.createElement('li');
        li.className = `severity-${inc.severity}`;
        li.innerHTML = `<strong>${inc.zone_name}</strong>: ${inc.description} <br><small>Severity: ${inc.severity} | ${new Date(inc.timestamp).toLocaleTimeString()}</small>`;
        list.appendChild(li);
    });
}
