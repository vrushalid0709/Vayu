// ── Navbar scroll effect ──────────────────────────────────────
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) navbar.classList.add('scrolled');
    else navbar.classList.remove('scrolled');
});

// ── Base URL — Java backend ───────────────────────────────────
const FLASK = "http://localhost:8080";

// ── Fetch current AQI + pollutants ───────────────────────────
async function loadCurrent() {
    try {
        const res  = await fetch(`${FLASK}/api/aqi`);
        const data = await res.json();

        // Hero section
        document.getElementById('hero-aqi').textContent    = data.aqi;
        document.getElementById('hero-pm25').innerHTML     = `${data.pm25} <span style="font-size:1rem;color:#64748b;">µg</span>`;
        document.getElementById('hero-label').textContent  = data.label;
        document.getElementById('hero-station').textContent = data.station;

        // Dashboard AQI circle
        document.getElementById('dash-aqi').textContent   = data.aqi;
        document.getElementById('dash-label').textContent = data.label;

        // Safe message
        document.getElementById('safe-msg').innerHTML =
            `<strong>${data.label}</strong><br>${getHealthMsg(data.aqi)}`;

        // Pollutant bars
        document.getElementById('val-pm25').textContent = `${data.pm25} µg`;
        document.getElementById('val-pm10').textContent = `${data.pm10} µg`;
        document.getElementById('val-no2').textContent  = `${data.no2} ppb`;
        document.getElementById('bar-pm25').style.width =
            `${Math.min((data.pm25 / 300) * 100, 100)}%`;
        document.getElementById('bar-pm10').style.width =
            `${Math.min((data.pm10 / 430) * 100, 100)}%`;
        document.getElementById('bar-no2').style.width  =
            `${Math.min((data.no2  / 200) * 100, 100)}%`;

        // AQI circle stroke color
        const circle = document.getElementById('aqi-circle-path');
        if (circle) {
            const pct = Math.min((data.aqi / 500) * 100, 100);
            circle.setAttribute('stroke-dasharray', `${pct}, 100`);
            circle.setAttribute('stroke', data.color || '#10b981');
        }

    } catch (e) {
        console.error('Current fetch failed:', e);
    }
}

// ── Fetch forecast ────────────────────────────────────────────
async function loadForecast() {
    try {
        const res  = await fetch(`${FLASK}/api/forecast`);
        const data = await res.json();

        const list = document.getElementById('forecast-list');
        if (!list) return;
        list.innerHTML = '';

        data.forecast.forEach(f => {
            const isWorst = f.hour === data.worst_hour.hour;
            list.innerHTML += `
                <div class="alert-item ${isWorst ? 'critical' : 'safe'}">
                    <div class="icon">${isWorst ? '⚠️' : '✅'}</div>
                    <div class="alert-content">
                        <strong>${f.hour} — AQI ${f.aqi}</strong>
                        <p>${f.label} air quality predicted</p>
                    </div>
                    <span class="alert-badge">${f.tag}</span>
                </div>`;
        });

        loadForecastChart(data);

    } catch (e) {
        console.error('Forecast fetch failed:', e);
    }
}

// ── Fetch advisory (Gemini AI) ────────────────────────────────
async function loadAdvisory() {
    try {
        const res  = await fetch(`${FLASK}/api/advisory`);
        const data = await res.json();

        const el = document.getElementById('ai-text');
        if (el && data.advisory) {
            el.innerHTML = `
                ${data.advisory}
                <br><br>
                <span style="font-size:0.8rem;opacity:0.7;">
                    📅 ${data.seasonal_insight} 
                    ${data.is_winter ? '❄️ Winter pollution season' : '🌿 Cleaner air season'}
                </span>`;
        }
    } catch (e) {
        console.error('Advisory fetch failed:', e);
    }
}

// ── Fetch activities ──────────────────────────────────────────
async function loadActivities() {
    const activities = [
        { name: 'walking', icon: '🚶', label: 'Walking',  duration: 30 },
        { name: 'running', icon: '🏃', label: 'Running',  duration: 30 },
        { name: 'cycling', icon: '🚴', label: 'Cycling',  duration: 30 },
    ];

    const grid = document.getElementById('activity-grid');
    if (!grid) return;
    grid.innerHTML = '';

    for (const act of activities) {
        try {
            const res  = await fetch(
                `${FLASK}/api/activity?name=${act.name}&duration=${act.duration}`
            );
            const data = await res.json();

            const badgeClass = data.safe ? 'safe' : 'avoid';
            const badgeText  = data.safe ? 'Safe' : 'Avoid';

            grid.innerHTML += `
                <div class="act-box">
                    <span class="act-icon">${act.icon}</span>
                    <div class="act-info">
                        <span class="activity-name">${act.label}</span>
                        <span class="badge ${badgeClass}">${badgeText}</span>
                    </div>
                </div>`;
        } catch (e) {
            console.error(`Activity fetch failed for ${act.name}:`, e);
        }
    }
}

// ── Forecast Chart ────────────────────────────────────────────
function loadForecastChart(data) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    if (window.trendChartInstance) {
        window.trendChartInstance.destroy();
    }

    const currentAqi = data.current_aqi;
    const labels = [
        'Now',
        data.forecast[0].hour,
        data.forecast[1].hour,
        data.forecast[2].hour
    ];
    const values = [
        currentAqi,
        data.forecast[0].aqi,
        data.forecast[1].aqi,
        data.forecast[2].aqi
    ];

    window.trendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'AQI Forecast',
                data: values,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointBackgroundColor: values.map(v =>
                    v > 200 ? '#ff0000' :
                    v > 100 ? '#ff9900' : '#10b981'
                ),
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15,23,42,0.9)',
                    padding: 12,
                    callbacks: {
                        label: ctx => `AQI: ${ctx.raw}`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(203,213,225,0.3)' },
                    ticks: { color: '#64748b' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b' }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// ── Health message helper ─────────────────────────────────────
function getHealthMsg(aqi) {
    if (aqi <= 50)  return 'Safe for all groups. Enjoy outdoor activities.';
    if (aqi <= 100) return 'Acceptable. Sensitive groups take care.';
    if (aqi <= 200) return 'Limit prolonged outdoor exposure.';
    if (aqi <= 300) return 'Avoid outdoor activity. Health risk for all.';
    return 'Emergency conditions. Stay indoors.';
}

// ── Load everything on page load ──────────────────────────────
window.addEventListener('DOMContentLoaded', async () => {
    await loadCurrent();
    await loadForecast();
    await loadAdvisory();
    await loadActivities();
    await loadSeasonal();

    // Refresh every 15 minutes
    setInterval(async () => {
        await loadCurrent();
        await loadForecast();
        await loadAdvisory();
        await loadActivities();
        await loadSeasonal();
    }, 900000);
});

// ── Fetch seasonal data + chart ───────────────────────────────
async function loadSeasonal() {
    try {
        const res  = await fetch(`${FLASK}/api/seasonal`);
        const data = await res.json();

        // Update insight text
        const insightEl = document.getElementById('seasonal-insight');
        if (insightEl) {
            insightEl.innerHTML = `
                <span style="color:#1a3a52;font-weight:600;">
                    📊 ${data.insight}
                </span>`;
        }

        // Build seasonal chart
        const ctx = document.getElementById('seasonalChart');
        if (!ctx) return;

        if (window.seasonalChartInstance) {
            window.seasonalChartInstance.destroy();
        }

        const labels = data.seasonal.map(d => d.month);
        const values = data.seasonal.map(d => d.aqi);
        const colors = data.seasonal.map(d => {
            if (d.season === 'Winter')       return '#ff4444';
            if (d.season === 'Post-Monsoon') return '#ff9900';
            if (d.season === 'Spring')       return '#ffff00';
            if (d.season === 'Summer')       return '#92d050';
            return '#00b050'; // Monsoon
        });

        // Highlight current month
        const currentMonth = new Date().toLocaleString('en',{month:'short'});
        const borderColors = labels.map(l =>
            l === currentMonth ? '#1a3a52' : 'transparent'
        );
        const borderWidths = labels.map(l =>
            l === currentMonth ? 3 : 0
        );

        window.seasonalChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average AQI',
                    data: values,
                    backgroundColor: colors,
                    borderColor: borderColors,
                    borderWidth: borderWidths,
                    borderRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx =>
                                `AQI: ${ctx.raw} (${data.seasonal[ctx.dataIndex].season})`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 200,
                        grid: { color: 'rgba(203,213,225,0.3)' },
                        ticks: { color: '#64748b' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#64748b' }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                }
            }
        });

    } catch (e) {
        console.error('Seasonal fetch failed:', e);
    }
}