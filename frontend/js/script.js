const accent = '#3b82f6';
const softAccent = 'rgba(59, 130, 246, 0.15)';
const gridColor = 'rgba(100, 116, 139, 0.15)';

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    resize: {
      duration: 0   // 🔥 stops infinite resize animation
    }
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#ffffff',
      titleColor: '#0f172a',
      bodyColor: '#334155',
      borderColor: 'rgba(59,130,246,0.2)',
      borderWidth: 1,
      cornerRadius: 10,
      padding: 10
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#64748b', font: { size: 11 } }
    },
    y: {
      grid: { color: 'rgba(100,116,139,0.15)' },
      border: { display: false },
      ticks: { color: '#64748b', font: { size: 11 } }
    }
  }
};


/* 🌊 AQI TREND LINE */
const aqiCtx = document.getElementById('aqiChart').getContext('2d');

const grad = aqiCtx.createLinearGradient(0, 0, 0, 300);
grad.addColorStop(0, softAccent);
grad.addColorStop(1, 'rgba(59,130,246,0)');

new Chart(aqiCtx, {
  type: 'line',
  data: {
    labels: ["01","02","03","04","05","06","07","08","09","10","11","12","13","14"],
    datasets: [{
      data: [70, 75, 80, 90, 100, 110, 120, 135, 145, 150, 155, 160, 162, 165],
      borderColor: accent,
      backgroundColor: grad,
      fill: true,
      borderWidth: 2.5,
      tension: 0.45,
      pointRadius: 0,
      pointHoverRadius: 4
    }]
  },
  options: chartOptions
});

/* 🍭 POLLUTANT BARS */
new Chart(document.getElementById('pollutantChart').getContext('2d'), {
  type: 'bar',
  data: {
    labels: ["PM2.5", "NO₂", "SO₂", "O₃"],
    datasets: [{
      data: [65, 38, 12, 25],
      backgroundColor: [
        accent,
        'rgba(59,130,246,0.6)',
        'rgba(59,130,246,0.4)',
        'rgba(59,130,246,0.5)'
      ],
      borderRadius: 8,
      borderSkipped: false
    }]
  },
  options: chartOptions
});
