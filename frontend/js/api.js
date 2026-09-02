const API_BASE_URL = window.location.origin;

class APIClient {
    static async request(endpoint, options = {}) {
        const token = localStorage.getItem('nirikshanx_token');
        const headers = options.headers || {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        options.headers = headers;

        try {
            const res = await fetch(`${API_BASE_URL}${endpoint}`, options);
            if (!res.ok) {
                const errData = await res.json().catch(() => ({ detail: 'Network response was not ok' }));
                throw new Error(errData.detail || 'API request failed');
            }
            return await res.json();
        } catch (err) {
            console.error(`API Error [${endpoint}]:`, err);
            throw err;
        }
    }

    static async getDashboardStats() {
        return this.request('/dashboard/stats');
    }

    static async uploadScan(formData) {
        return this.request('/scans/upload', {
            method: 'POST',
            body: formData
        });
    }

    static async getScanDetails(scanId) {
        return this.request(`/scans/${scanId}`);
    }

    static async listScans() {
        return this.request('/scans/');
    }
}
