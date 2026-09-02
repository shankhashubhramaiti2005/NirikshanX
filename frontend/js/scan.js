async function handleScanSubmit(event) {
    event.preventDefault();
    const fileInput = document.getElementById('scan-file-input');
    const categorySelect = document.getElementById('scan-category-select');
    const resultContainer = document.getElementById('scan-results');

    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please select an image file first.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('category', categorySelect.value || 'general');

    resultContainer.innerHTML = `<div class="spinner"></div> Running 4-Step AI Compliance Pipeline...`;

    try {
        const response = await APIClient.uploadScan(formData);
        renderScanResult(response, resultContainer);
        if (typeof loadDashboardStats === 'function') {
            loadDashboardStats();
        }
    } catch (err) {
        resultContainer.innerHTML = `
            <div class="alert alert-danger">
                <strong>Error:</strong> ${err.message}
            </div>
        `;
    }
}

function renderScanResult(data, container) {
    const res = data.result || {};
    const isPass = res.is_valid;
    
    container.innerHTML = `
        <div class="card result-card ${isPass ? 'border-success' : 'border-danger'}">
            <h3>Scan Result: <span class="${isPass ? 'text-success' : 'text-danger'}">${isPass ? 'COMPLIANT' : 'NON-COMPLIANT'}</span></h3>
            <p><strong>Scan ID:</strong> #${data.scan_id} | <strong>Processing Time:</strong> ${res.processing_time_seconds || 0}s</p>
            
            <h4>Extracted Declarations</h4>
            <ul>
                <li><strong>MRP:</strong> ${res.ocr_metrics?.declarations?.mrp || 'Not Found'}</li>
                <li><strong>Net Quantity:</strong> ${res.ocr_metrics?.declarations?.net_quantity || 'Not Found'}</li>
                <li><strong>MFD Date:</strong> ${res.ocr_metrics?.declarations?.mfd_date || 'Not Found'}</li>
                <li><strong>Expiry Date:</strong> ${res.ocr_metrics?.declarations?.expiry_date || 'Not Found'}</li>
                <li><strong>Country of Origin:</strong> ${res.ocr_metrics?.declarations?.country_of_origin || 'Not Found'}</li>
            </ul>

            ${res.reasons && res.reasons.length > 0 ? `
                <h4 class="text-danger">Violations / Issues</h4>
                <ul>
                    ${res.reasons.map(r => `<li class="text-danger">${escapeHtml(r)}</li>`).join('')}
                </ul>
            ` : ''}

            <a href="/reports/pdf/${data.scan_id}" target="_blank" class="btn btn-primary mt-2">Download Official PDF Report</a>
        </div>
    `;
}
