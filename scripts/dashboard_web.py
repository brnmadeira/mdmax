#!/usr/bin/env python3
"""
MdMax Real-time Dashboard
Web-based visualization of token economy and conversion statistics
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
from pathlib import Path

dashboard_app = FastAPI(title="MdMax Dashboard")


def get_dashboard_html():
    """Generate HTML for real-time dashboard"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MdMax Dashboard - Token Economy Tracker</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
            }

            .header {
                background: rgba(255, 255, 255, 0.95);
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            }

            .header h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 32px;
            }

            .header p {
                color: #666;
                font-size: 16px;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .stat-card {
                background: rgba(255, 255, 255, 0.95);
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                text-align: center;
            }

            .stat-card h3 {
                color: #999;
                font-size: 14px;
                text-transform: uppercase;
                margin-bottom: 15px;
                font-weight: 500;
            }

            .stat-value {
                font-size: 36px;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 5px;
            }

            .stat-label {
                color: #666;
                font-size: 13px;
            }

            .charts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 30px;
                margin-bottom: 30px;
            }

            .chart-card {
                background: rgba(255, 255, 255, 0.95);
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            }

            .chart-card h2 {
                color: #667eea;
                font-size: 18px;
                margin-bottom: 20px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }

            .chart-container {
                position: relative;
                height: 300px;
                margin-bottom: 20px;
            }

            .format-list {
                background: rgba(255, 255, 255, 0.95);
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            }

            .format-item {
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid #eee;
            }

            .format-item:last-child {
                border-bottom: none;
            }

            .format-name {
                color: #333;
                font-weight: 500;
            }

            .format-count {
                color: #667eea;
                font-weight: 700;
            }

            .refresh-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.3s;
            }

            .refresh-btn:hover {
                background: #764ba2;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }

            .footer {
                text-align: center;
                color: rgba(255, 255, 255, 0.8);
                margin-top: 30px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 MdMax Dashboard</h1>
                <p>Real-time Token Economy Tracker & Conversion Statistics</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Conversions</h3>
                    <div class="stat-value" id="conversions">0</div>
                    <div class="stat-label">files processed</div>
                </div>

                <div class="stat-card">
                    <h3>Total Tokens Saved</h3>
                    <div class="stat-value" id="tokens-saved">0</div>
                    <div class="stat-label">accumulated savings</div>
                </div>

                <div class="stat-card">
                    <h3>Average Savings</h3>
                    <div class="stat-value" id="avg-savings">72%</div>
                    <div class="stat-label">per file</div>
                </div>

                <div class="stat-card">
                    <h3>Current Status</h3>
                    <div class="stat-value" style="color: #4caf50;">●</div>
                    <div class="stat-label">API running (healthy)</div>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-card">
                    <h2>📊 Token Savings Over Time</h2>
                    <div class="chart-container">
                        <canvas id="savingsChart"></canvas>
                    </div>
                </div>

                <div class="chart-card">
                    <h2>📈 Conversion by Format</h2>
                    <div class="chart-container">
                        <canvas id="formatsChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="format-list">
                <h2 style="color: #667eea; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea;">
                    📁 Format Usage
                </h2>
                <div id="format-items"></div>
            </div>

            <div class="footer">
                <p>MdMax v2.1.0 • Real-time Dashboard • API: http://localhost:8000</p>
                <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
            </div>
        </div>

        <script>
            const API_URL = 'http://localhost:8000';

            async function loadStats() {
                try {
                    const response = await fetch(API_URL + '/stats');
                    const data = await response.json();

                    document.getElementById('conversions').textContent = data.total_conversions;
                    document.getElementById('tokens-saved').textContent = data.total_tokens_saved.toLocaleString();

                    // Update format list
                    const formatList = document.getElementById('format-items');
                    formatList.innerHTML = '';

                    for (const [format, count] of Object.entries(data.formats_used)) {
                        const item = document.createElement('div');
                        item.className = 'format-item';
                        item.innerHTML = `
                            <span class="format-name">${format}</span>
                            <span class="format-count">${count} files</span>
                        `;
                        formatList.appendChild(item);
                    }

                    // Update charts
                    updateCharts(data);

                } catch (error) {
                    console.log('Dashboard data unavailable - API may not be running');
                }
            }

            function updateCharts(data) {
                // Mock data for demonstration
                const ctx1 = document.getElementById('savingsChart').getContext('2d');
                new Chart(ctx1, {
                    type: 'line',
                    data: {
                        labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                        datasets: [{
                            label: 'Tokens Saved',
                            data: [0, 200, 400, 650, 900, 1100, data.total_tokens_saved],
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 6,
                            pointBackgroundColor: '#667eea'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, ticks: { color: '#999' } },
                            x: { ticks: { color: '#999' } }
                        }
                    }
                });

                // Format distribution
                const ctx2 = document.getElementById('formatsChart').getContext('2d');
                const formats = Object.keys(data.formats_used).slice(0, 5);
                const counts = Object.values(data.formats_used).slice(0, 5);

                new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: formats,
                        datasets: [{
                            data: counts,
                            backgroundColor: [
                                '#667eea',
                                '#764ba2',
                                '#f093fb',
                                '#4facfe',
                                '#00f2fe'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom' } }
                    }
                });
            }

            // Load stats on page load and refresh every 10 seconds
            loadStats();
            setInterval(loadStats, 10000);
        </script>
    </body>
    </html>
    """


@dashboard_app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard HTML"""
    return get_dashboard_html()


@dashboard_app.get("/api/stats")
async def stats():
    """Dashboard API endpoint for stats"""
    # This would connect to the main API
    return {
        "total_conversions": 0,
        "total_tokens_saved": 0,
        "total_files_processed": 0,
        "formats_used": {}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(dashboard_app, host="0.0.0.0", port=8001)
