async function loadDashboard() {
  const monthlyChartEl = document.getElementById('monthlyChart');
  const statusChartEl = document.getElementById('statusChart');
  if (!monthlyChartEl && !statusChartEl) return;

  const response = await fetch('/dashboard/data');
  const data = await response.json();

  if (monthlyChartEl) {
    new Chart(monthlyChartEl, {
      type: 'line',
      data: {
        labels: data.monthly.map(x => x.month),
        datasets: [{ label: 'Complaints', data: data.monthly.map(x => x.count), borderColor: '#1f6feb' }]
      }
    });
  }

  if (statusChartEl) {
    new Chart(statusChartEl, {
      type: 'doughnut',
      data: {
        labels: data.statuses.map(x => x.status),
        datasets: [{ data: data.statuses.map(x => x.count), backgroundColor: ['#f1b825', '#1f6feb', '#159fbc', '#2ea043'] }]
      }
    });
  }
}

async function bindServiceDropdown() {
  const depSelect = document.getElementById('departmentSelect');
  const serviceSelect = document.getElementById('serviceSelect');
  if (!depSelect || !serviceSelect) return;

  depSelect.addEventListener('change', async () => {
    const res = await fetch(`/services/${depSelect.value}`);
    const list = await res.json();
    serviceSelect.innerHTML = '';
    list.forEach(item => {
      const opt = document.createElement('option');
      opt.value = item.id;
      opt.textContent = item.name;
      serviceSelect.appendChild(opt);
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
  bindServiceDropdown();
});
