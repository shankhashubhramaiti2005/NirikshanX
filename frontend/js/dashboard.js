/**
 * NirikshanX Dashboard & Chart.js Visualizations Module
 */
import { apiFetch } from './api.js';

let statusChartInstance = null;
let categoryChartInstance = null;

export async function fetchDashboardStats() {
  return await apiFetch('/dashboard/stats');
}

export function renderDashboardCharts(stats) {
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js library not loaded');
    return;
  }

  // 1. Status Donut Chart
  const statusCanvas = document.getElementById('statusChart');
  if (statusCanvas) {
    if (statusChartInstance) statusChartInstance.destroy();
    
    statusChartInstance = new Chart(statusCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Compliant', 'Violations', 'Pending Review'],
        datasets: [{
          data: [
            stats.compliant || 0,
            stats.violations || 0,
            stats.pending_review || 0
          ],
          backgroundColor: ['#10B981', '#EF4444', '#F59E0B'],
          borderWidth: 0,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }

  // 2. Category Bar Chart
  const catCanvas = document.getElementById('categoryChart');
  if (catCanvas) {
    if (categoryChartInstance) categoryChartInstance.destroy();

    const catData = stats.by_category || [];
    const labels = catData.map(c => c.category);
    const counts = catData.map(c => c.count);

    categoryChartInstance = new Chart(catCanvas, {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['FOOD', 'GENERAL', 'COSMETICS'],
        datasets: [{
          label: 'Scans per Category',
          data: counts.length ? counts : [0, 0, 0],
          backgroundColor: '#3B82F6',
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
  }
}
