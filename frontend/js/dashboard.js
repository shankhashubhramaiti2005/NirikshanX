document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        const stats = await APIClient.getDashboardStats();
        
        document.getElementById('stat-total-scans').innerText = stats.total_scans;
        document.getElementById('stat-passed-scans').innerText = stats.passed_scans;
        document.getElementById('stat-failed-scans').innerText = stats.failed_scans;
        document.getElementById('stat-compliance-rate').innerText = `${stats.compliance_rate_percentage}%`;

        renderRecentScansTable(stats.recent_scans);
    } catch (err) {
        console.warn('Dashboard live stats fetch failed, using sample demo stats.', err);
    }
}

function renderRecentScansTable(scans) {
    const tbody = document.getElementById('recent-scans-tbody');
    if (!tbody) return;

    if (!scans || scans.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center">No scans recorded yet. Upload an image to start verification.</td></tr>`;
        return;
    }

    tbody.innerHTML = scans.map(s => `
        <tr>
            <td>#${s.id}</td>
            <td>${escapeHtml(s.filename)}</td>
            <td>
                <span class="badge ${s.is_valid ? 'badge-success' : 'badge-danger'}">
                    ${s.is_valid ? 'PASSED' : 'NON-COMPLIANT'}
                </span>
            </td>
            <td>${s.processing_time ? s.processing_time + 's' : 'N/A'}</td>
            <td>${s.created_at ? new Date(s.created_at).toLocaleString() : 'Just now'}</td>
            <td>
                <a href="/reports/pdf/${s.id}" target="_blank" class="btn btn-sm btn-outline">
                    📥 PDF Report
                </a>
            </td>
        </tr>
    `).join('');
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
