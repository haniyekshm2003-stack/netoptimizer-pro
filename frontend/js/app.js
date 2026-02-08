/**
 * NetOptimizer Pro - Frontend Application
 * ========================================
 * Advanced network analysis dashboard
 */

class NetworkAnalyzer {
    constructor() {
        this.apiBase = '';  // Same origin
        this.currentPage = 'dashboard';
        this.testResults = {
            network: null,
            dns: null,
            cdn: null,
            ping: null,
            protocol: null,
            ports: null,
            recommendations: null
        };

        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupEventListeners();
        this.initCharts();
        this.checkConnection();
    }

    // ===== Navigation =====
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');

        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                this.navigateTo(page);
            });
        });
    }

    navigateTo(page) {
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });

        // Update pages
        document.querySelectorAll('.page').forEach(p => {
            p.classList.toggle('active', p.id === `${page}-page`);
        });

        // Update title
        const titles = {
            dashboard: 'Dashboard',
            network: 'Network Analysis',
            dns: 'DNS Benchmark',
            cdn: 'CDN Testing',
            ping: 'Global Ping',
            protocol: 'Protocol Test',
            ports: 'Port Scanner',
            recommendations: 'Recommendations',
            reports: 'Reports'
        };

        document.getElementById('page-title').textContent = titles[page] || page;
        this.currentPage = page;
    }

    // ===== Event Listeners =====
    setupEventListeners() {
        // Run all tests
        document.getElementById('run-all-tests')?.addEventListener('click', () => this.runAllTests());

        // Network scan
        document.getElementById('run-network-scan')?.addEventListener('click', () => this.runNetworkScan());

        // DNS benchmark
        document.getElementById('run-dns-benchmark')?.addEventListener('click', () => this.runDNSBenchmark());

        // CDN test
        document.getElementById('run-cdn-test')?.addEventListener('click', () => this.runCDNTest());

        // Ping test
        document.getElementById('run-ping-test')?.addEventListener('click', () => this.runPingTest());

        // Protocol test
        document.getElementById('run-protocol-test')?.addEventListener('click', () => this.runProtocolTest());

        // Port scan
        document.getElementById('run-port-scan')?.addEventListener('click', () => this.runPortScan());

        // Recommendations
        document.getElementById('get-recommendations')?.addEventListener('click', () => this.getRecommendations());

        // Export buttons
        document.getElementById('export-json')?.addEventListener('click', () => this.exportJSON());
        document.getElementById('export-csv')?.addEventListener('click', () => this.exportCSV());
        document.getElementById('generate-report')?.addEventListener('click', () => this.generateReport());
    }

    // ===== API Methods =====
    async apiCall(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.apiBase}${endpoint}`, options);

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    // ===== Test Methods =====
    async runAllTests() {
        this.showLoading('Running all tests...');

        try {
            await this.runNetworkScan();
            await this.runDNSBenchmark();
            await this.runCDNTest();
            await this.runPingTest();
            await this.runProtocolTest();
            await this.getRecommendations();

            this.showToast('All tests completed successfully!', 'success');
            this.updateDashboard();
        } catch (error) {
            this.showToast('Some tests failed. Check results.', 'warning');
        } finally {
            this.hideLoading();
        }
    }

    async runNetworkScan() {
        this.showLoading('Scanning network...');

        try {
            const result = await this.apiCall('/api/network/scan');
            this.testResults.network = result;
            this.displayNetworkResults(result);
            this.showToast('Network scan complete', 'success');
            return result;
        } catch (error) {
            this.showToast('Network scan failed', 'error');
            this.displayNetworkError();
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    async runDNSBenchmark() {
        this.showLoading('Benchmarking DNS servers...');

        try {
            const result = await this.apiCall('/api/dns/benchmark');
            this.testResults.dns = result;
            this.displayDNSResults(result);
            this.showToast('DNS benchmark complete', 'success');
            return result;
        } catch (error) {
            this.showToast('DNS benchmark failed', 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    async runCDNTest() {
        this.showLoading('Testing CDN providers...');

        try {
            const result = await this.apiCall('/api/cdn/test');
            this.testResults.cdn = result;
            this.displayCDNResults(result);
            this.showToast('CDN test complete', 'success');
            return result;
        } catch (error) {
            this.showToast('CDN test failed', 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    async runPingTest() {
        this.showLoading('Testing global latency...');

        try {
            const result = await this.apiCall('/api/ping/all');
            this.testResults.ping = result;
            this.displayPingResults(result);
            this.showToast('Global ping test complete', 'success');
            return result;
        } catch (error) {
            this.showToast('Ping test failed', 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    async runProtocolTest() {
        this.showLoading('Testing protocols...');

        try {
            const result = await this.apiCall('/api/protocol/benchmark');
            this.testResults.protocol = result;
            this.displayProtocolResults(result);
            this.showToast('Protocol test complete', 'success');
            return result;
        } catch (error) {
            this.showToast('Protocol test failed', 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    async runPortScan() {
        const target = document.getElementById('scan-target')?.value || 'localhost';
        const scanType = document.getElementById('scan-type')?.value || 'common';

        this.showLoading(`Scanning ports on ${target}...`);

        try {
            const result = await this.apiCall('/api/ports/scan', 'POST', {
                target,
                scan_type: scanType
            });
            this.testResults.ports = result;
            this.displayPortResults(result);
            this.showToast('Port scan complete', 'success');
            return result;
        } catch (error) {
            this.showToast('Port scan failed', 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    async getRecommendations() {
        this.showLoading('Analyzing data...');

        try {
            const result = await this.apiCall('/api/recommendations');
            this.testResults.recommendations = result;
            this.displayRecommendations(result);
            this.showToast('Recommendations generated', 'success');
            return result;
        } catch (error) {
            this.showToast('Analysis failed', 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    // ===== Display Methods =====
    displayNetworkResults(data) {
        const container = document.getElementById('network-results');
        if (!container) return;

        const html = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-network-wired"></i></div>
                    <div class="stat-info">
                        <h3>Public IP</h3>
                        <p class="stat-value">${data.public_ip || 'N/A'}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-clock"></i></div>
                    <div class="stat-info">
                        <h3>Latency</h3>
                        <p class="stat-value">${data.latency_ms || 'N/A'} ms</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-download"></i></div>
                    <div class="stat-info">
                        <h3>Download Speed</h3>
                        <p class="stat-value">${data.download_mbps?.toFixed(2) || 'N/A'} Mbps</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-upload"></i></div>
                    <div class="stat-info">
                        <h3>Upload Speed</h3>
                        <p class="stat-value">${data.upload_mbps?.toFixed(2) || 'N/A'} Mbps</p>
                    </div>
                </div>
            </div>
            <div class="card" style="margin-top: 20px;">
                <div class="card-header"><h3>Details</h3></div>
                <div class="card-body">
                    <table class="results-table">
                        <tr><td>MTU</td><td>${data.mtu || 'N/A'}</td></tr>
                        <tr><td>NAT Type</td><td>${data.nat_type || 'N/A'}</td></tr>
                        <tr><td>ISP</td><td>${data.isp || 'N/A'}</td></tr>
                        <tr><td>Location</td><td>${data.location || 'N/A'}</td></tr>
                    </table>
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Update dashboard
        document.getElementById('dashboard-latency').textContent = `${data.latency_ms || '--'} ms`;
        document.getElementById('dashboard-download').textContent = `${data.download_mbps?.toFixed(2) || '--'} Mbps`;
        document.getElementById('dashboard-upload').textContent = `${data.upload_mbps?.toFixed(2) || '--'} Mbps`;
    }

    displayNetworkError() {
        const container = document.getElementById('network-results');
        if (container) {
            container.innerHTML = `<p class="placeholder-text" style="color: var(--accent-danger);">Failed to scan network. Check your connection.</p>`;
        }
    }

    displayDNSResults(data) {
        const container = document.getElementById('dns-results');
        if (!container) return;

        let html = '';
        const servers = data.servers || {};
        let rank = 1;

        for (const [name, info] of Object.entries(servers)) {
            html += `
                <div class="dns-server-card">
                    <div class="dns-server-info">
                        <div class="dns-server-rank">${rank}</div>
                        <div>
                            <div class="dns-server-name">${name}</div>
                            <div class="dns-server-ip">${info.ip || 'N/A'}</div>
                        </div>
                    </div>
                    <div class="dns-server-stats">
                        <div class="dns-stat">
                            <div class="dns-stat-value">${info.avg_response_time || 'N/A'}</div>
                            <div class="dns-stat-label">AVG (ms)</div>
                        </div>
                        <div class="dns-stat">
                            <div class="dns-stat-value">${info.success_rate || 'N/A'}%</div>
                            <div class="dns-stat-label">Success</div>
                        </div>
                        <div class="dns-stat">
                            <div class="dns-stat-value">${info.reliability_score || 'N/A'}</div>
                            <div class="dns-stat-label">Score</div>
                        </div>
                    </div>
                </div>
            `;
            rank++;
        }

        container.innerHTML = html || '<p class="placeholder-text">No DNS results available</p>';

        // Update dashboard
        const best = data.best_server;
        if (best) {
            document.getElementById('dashboard-dns').textContent = best.name || '--';
        }
    }

    displayCDNResults(data) {
        const container = document.getElementById('cdn-results');
        if (!container) return;

        let html = '<table class="results-table"><thead><tr><th>Provider</th><th>Avg Time</th><th>Success</th><th>Score</th></tr></thead><tbody>';

        const providers = data.providers || {};

        for (const [name, info] of Object.entries(providers)) {
            html += `
                <tr>
                    <td><strong>${name}</strong></td>
                    <td>${info.avg_response_time || 'N/A'} ms</td>
                    <td>${info.success_rate || 'N/A'}%</td>
                    <td>${info.score || 'N/A'}</td>
                </tr>
            `;
        }

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    displayPingResults(data) {
        const container = document.getElementById('ping-results');
        if (!container) return;

        let html = '<table class="results-table"><thead><tr><th>Region</th><th>Location</th><th>Provider</th><th>Latency</th></tr></thead><tbody>';

        const regions = data.regions || {};

        for (const [name, info] of Object.entries(regions)) {
            const latencyClass = info.avg_latency_ms < 50 ? 'status-open' :
                                 info.avg_latency_ms < 150 ? 'status-filtered' : 'status-closed';

            html += `
                <tr>
                    <td><strong>${name}</strong></td>
                    <td>${info.location || 'N/A'}</td>
                    <td>${info.provider || 'N/A'}</td>
                    <td class="${latencyClass}">${info.avg_latency_ms || 'N/A'} ms</td>
                </tr>
            `;
        }

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    displayProtocolResults(data) {
        const container = document.getElementById('protocol-results');
        if (!container) return;

        const summary = data.summary || {};

        let html = '<table class="results-table"><thead><tr><th>Protocol</th><th>Avg Time</th><th>Success Rate</th><th>Tests</th></tr></thead><tbody>';

        for (const [protocol, info] of Object.entries(summary)) {
            html += `
                <tr>
                    <td><strong>${protocol.toUpperCase()}</strong></td>
                    <td>${info.avg_time_ms || 'N/A'} ms</td>
                    <td>${info.success_rate || 'N/A'}%</td>
                    <td>${info.tests_passed || 0}/${info.tests_total || 0}</td>
                </tr>
            `;
        }

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    displayPortResults(data) {
        const container = document.getElementById('port-results');
        if (!container) return;

        const summary = data.summary || {};

        let html = `
            <div class="stats-grid" style="margin-bottom: 20px;">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-door-open"></i></div>
                    <div class="stat-info">
                        <h3>Open Ports</h3>
                        <p class="stat-value" style="color: var(--accent-success);">${summary.open || 0}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-door-closed"></i></div>
                    <div class="stat-info">
                        <h3>Closed Ports</h3>
                        <p class="stat-value" style="color: var(--accent-danger);">${summary.closed || 0}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-filter"></i></div>
                    <div class="stat-info">
                        <h3>Filtered</h3>
                        <p class="stat-value" style="color: var(--accent-warning);">${summary.filtered || 0}</p>
                    </div>
                </div>
            </div>
        `;

        html += '<table class="results-table"><thead><tr><th>Port</th><th>Status</th><th>Service</th><th>Category</th></tr></thead><tbody>';

        const results = data.results || [];

        for (const port of results) {
            const statusClass = port.status === 'open' ? 'status-open' :
                               port.status === 'closed' ? 'status-closed' : 'status-filtered';

            html += `
                <tr>
                    <td><strong>${port.port}</strong></td>
                    <td class="${statusClass}">${port.status}</td>
                    <td>${port.service || 'Unknown'}</td>
                    <td>${port.category || 'N/A'}</td>
                </tr>
            `;
        }

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    displayRecommendations(data) {
        const container = document.getElementById('recommendations-results');
        if (!container) return;

        const recommendations = data.recommendations || {};

        let html = `
            <div class="stats-grid" style="margin-bottom: 20px;">
                <div class="stat-card">
                    <div class="stat-icon" style="background: linear-gradient(135deg, #f85149 0%, #ff7b72 100%);"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="stat-info">
                        <h3>High Priority</h3>
                        <p class="stat-value">${data.high_priority || 0}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: linear-gradient(135deg, #d29922 0%, #f0c14b 100%);"><i class="fas fa-exclamation-circle"></i></div>
                    <div class="stat-info">
                        <h3>Medium Priority</h3>
                        <p class="stat-value">${data.medium_priority || 0}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: linear-gradient(135deg, #3fb950 0%, #56d364 100%);"><i class="fas fa-info-circle"></i></div>
                    <div class="stat-info">
                        <h3>Low Priority</h3>
                        <p class="stat-value">${data.low_priority || 0}</p>
                    </div>
                </div>
            </div>
        `;

        // High priority
        if (recommendations.high?.length) {
            html += '<h4 style="margin: 20px 0 10px;">High Priority</h4>';
            for (const rec of recommendations.high) {
                html += this.createRecommendationCard(rec, 'high');
            }
        }

        // Medium priority
        if (recommendations.medium?.length) {
            html += '<h4 style="margin: 20px 0 10px;">Medium Priority</h4>';
            for (const rec of recommendations.medium) {
                html += this.createRecommendationCard(rec, 'medium');
            }
        }

        // Low priority
        if (recommendations.low?.length) {
            html += '<h4 style="margin: 20px 0 10px;">Low Priority</h4>';
            for (const rec of recommendations.low) {
                html += this.createRecommendationCard(rec, 'low');
            }
        }

        container.innerHTML = html || '<p class="placeholder-text">No recommendations available. Run tests first.</p>';
    }

    createRecommendationCard(rec, priority) {
        return `
            <div class="recommendation-card ${priority}">
                <div class="recommendation-header">
                    <span class="recommendation-title">${rec.title}</span>
                    <span class="recommendation-priority ${priority}">${priority}</span>
                </div>
                <p class="recommendation-description">${rec.description}</p>
                <p class="recommendation-action"><i class="fas fa-arrow-right"></i> ${rec.action}</p>
            </div>
        `;
    }

    updateDashboard() {
        const quickStatus = document.getElementById('quick-status');
        if (!quickStatus) return;

        let html = '';

        if (this.testResults.network) {
            const n = this.testResults.network;
            const latencyClass = n.latency_ms < 50 ? 'good' : n.latency_ms < 150 ? 'warning' : 'bad';

            html += `
                <div class="quick-status-item">
                    <span class="label">Network Latency</span>
                    <span class="value ${latencyClass}">${n.latency_ms || '--'} ms</span>
                </div>
            `;
        }

        if (this.testResults.dns?.best_server) {
            html += `
                <div class="quick-status-item">
                    <span class="label">Best DNS</span>
                    <span class="value good">${this.testResults.dns.best_server.name}</span>
                </div>
            `;
        }

        if (this.testResults.ping?.fastest_region) {
            html += `
                <div class="quick-status-item">
                    <span class="label">Fastest Region</span>
                    <span class="value good">${this.testResults.ping.fastest_region.name}</span>
                </div>
            `;
        }

        if (this.testResults.recommendations) {
            const high = this.testResults.recommendations.high_priority || 0;
            const statusClass = high === 0 ? 'good' : high < 3 ? 'warning' : 'bad';

            html += `
                <div class="quick-status-item">
                    <span class="label">Issues Found</span>
                    <span class="value ${statusClass}">${high} critical</span>
                </div>
            `;
        }

        quickStatus.innerHTML = html || '<p>Run tests to see your network status...</p>';
    }

    // ===== Charts =====
    initCharts() {
        const ctx = document.getElementById('performance-chart')?.getContext('2d');
        if (!ctx) return;

        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['DNS', 'CDN', 'TCP', 'TLS', 'HTTP', 'HTTPS'],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [0, 0, 0, 0, 0, 0],
                    borderColor: '#58a6ff',
                    backgroundColor: 'rgba(88, 166, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(48, 54, 61, 0.5)'
                        },
                        ticks: {
                            color: '#8b949e'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(48, 54, 61, 0.5)'
                        },
                        ticks: {
                            color: '#8b949e'
                        }
                    }
                }
            }
        });
    }

    // ===== Export Methods =====
    exportJSON() {
        const data = JSON.stringify(this.testResults, null, 2);
        this.downloadFile(data, 'network-report.json', 'application/json');
        this.showToast('JSON exported', 'success');
    }

    exportCSV() {
        let csv = 'Test,Metric,Value\n';

        if (this.testResults.network) {
            const n = this.testResults.network;
            csv += `Network,Latency,${n.latency_ms}\n`;
            csv += `Network,Download,${n.download_mbps}\n`;
            csv += `Network,Upload,${n.upload_mbps}\n`;
        }

        if (this.testResults.dns?.servers) {
            for (const [name, info] of Object.entries(this.testResults.dns.servers)) {
                csv += `DNS,${name},${info.avg_response_time}\n`;
            }
        }

        this.downloadFile(csv, 'network-report.csv', 'text/csv');
        this.showToast('CSV exported', 'success');
    }

    generateReport() {
        const preview = document.getElementById('report-preview');
        if (!preview) return;

        let html = '<div style="font-family: monospace; white-space: pre-wrap;">';
        html += '='.repeat(50) + '\n';
        html += '        NETOPTIMIZER PRO - NETWORK REPORT\n';
        html += '='.repeat(50) + '\n\n';
        html += `Generated: ${new Date().toLocaleString()}\n\n`;

        if (this.testResults.network) {
            html += '--- NETWORK STATUS ---\n';
            html += `Latency: ${this.testResults.network.latency_ms} ms\n`;
            html += `Download: ${this.testResults.network.download_mbps?.toFixed(2)} Mbps\n`;
            html += `Upload: ${this.testResults.network.upload_mbps?.toFixed(2)} Mbps\n\n`;
        }

        if (this.testResults.dns?.best_server) {
            html += '--- DNS RECOMMENDATION ---\n';
            html += `Best Server: ${this.testResults.dns.best_server.name}\n`;
            html += `Response Time: ${this.testResults.dns.best_server.avg_response_time} ms\n\n`;
        }

        if (this.testResults.recommendations) {
            html += '--- RECOMMENDATIONS ---\n';
            html += `High Priority: ${this.testResults.recommendations.high_priority}\n`;
            html += `Medium Priority: ${this.testResults.recommendations.medium_priority}\n`;
            html += `Low Priority: ${this.testResults.recommendations.low_priority}\n`;
        }

        html += '</div>';
        preview.innerHTML = html;
        this.showToast('Report generated', 'success');
    }

    downloadFile(content, filename, type) {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    // ===== Utility Methods =====
    async checkConnection() {
        try {
            await this.apiCall('/api/health');
            this.setConnectionStatus(true);
        } catch {
            this.setConnectionStatus(false);
        }
    }

    setConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        if (!indicator) return;

        const dot = indicator.querySelector('.status-dot');
        const text = indicator.querySelector('span:last-child');

        if (connected) {
            dot.style.background = 'var(--accent-success)';
            text.textContent = 'Connected';
        } else {
            dot.style.background = 'var(--accent-danger)';
            text.textContent = 'Disconnected';
        }
    }

    showLoading(text = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');

        if (overlay) overlay.classList.add('active');
        if (loadingText) loadingText.textContent = text;
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.remove('active');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icon = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        }[type] || 'fa-info-circle';

        toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.app = new NetworkAnalyzer();
});
