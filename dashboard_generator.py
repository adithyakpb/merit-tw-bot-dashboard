import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from metrics_processor import MetricsProcessor

class DashboardGenerator:
    """
    Generates the monitoring dashboard.
    """
    
    def __init__(self, metrics_processor: MetricsProcessor):
        """
        Initialize the dashboard generator.
        
        Args:
            metrics_processor: The metrics processor to use
        """
        self.metrics_processor = metrics_processor
        
    def generate_dashboard(self, output_path: str = "mongodb_dashboard.html") -> str:
        """
        Generate the dashboard HTML.
        
        Args:
            output_path: Path to save the dashboard HTML
            
        Returns:
            Path to the generated dashboard
        """
        # Get metrics
        metrics = self.metrics_processor.calculate_metrics()
        
        # Format data for the dashboard
        dashboard_data = self._format_dashboard_data(metrics)
        
        # Generate HTML
        html = self._generate_html(dashboard_data)
        
        # Save to file
        with open(output_path, "w") as f:
            f.write(html)
        
        return output_path
    
    def _format_dashboard_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format metrics data for the dashboard.
        
        Args:
            metrics: Calculated metrics
            
        Returns:
            Formatted data for the dashboard
        """
        # Extract usage metrics
        usage = metrics.get("usage", {})
        performance = metrics.get("performance", {})
        model = metrics.get("model", {})
        user = metrics.get("user", {})
        
        # Format summary metrics
        summary = {
            "total_sessions": usage.get("total_sessions", 0),
            "active_sessions": usage.get("active_sessions", 0),
            "user_messages": usage.get("user_messages", 0),
            "assistant_messages": usage.get("assistant_messages", 0),
            "avg_processing_time": performance.get("processing_time", {}).get("avg", 0),
            "token_efficiency": performance.get("token_efficiency", 0),
            "unique_users": user.get("unique_users", 0)
        }
        
        # Format time series data
        time_series = self._format_time_series(usage.get("daily", []))
        
        # Format model data
        model_data = self._format_model_data(model)
        
        # Format user data
        user_data = self._format_user_data(user)
        
        # Format performance data
        performance_data = self._format_performance_data(performance)
        
        # Combine all data
        return {
            "summary": summary,
            "time_series": time_series,
            "model": model_data,
            "user": user_data,
            "performance": performance_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_time_series(self, daily_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format time series data.
        
        Args:
            daily_data: Daily metrics data
            
        Returns:
            Formatted time series data
        """
        dates = []
        user_messages = []
        assistant_messages = []
        total_tokens = []
        processing_times = []
        
        for day in daily_data:
            dates.append(day.get("date", ""))
            
            messages = day.get("messages", {})
            user_messages.append(messages.get("user", 0))
            assistant_messages.append(messages.get("assistant", 0))
            
            total_tokens.append(day.get("total_tokens", 0))
            processing_times.append(day.get("avg_processing_time", 0))
        
        return {
            "dates": dates,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_tokens": total_tokens,
            "processing_times": processing_times
        }
    
    def _format_model_data(self, model_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format model data.
        
        Args:
            model_metrics: Model metrics
            
        Returns:
            Formatted model data
        """
        model_usage = model_metrics.get("model_usage", {})
        model_tokens = model_metrics.get("model_tokens", {})
        model_cost = model_metrics.get("model_cost", {})
        
        # Format for pie charts
        models = list(model_usage.keys())
        usage_counts = list(model_usage.values())
        
        # Format token usage by model
        token_data = []
        
        for model, tokens in model_tokens.items():
            token_data.append({
                "model": model,
                "prompt": tokens.get("prompt", 0),
                "completion": tokens.get("completion", 0),
                "total": tokens.get("total", 0)
            })
        
        # Format cost data
        cost_data = []
        
        for model, cost in model_cost.items():
            cost_data.append({
                "model": model,
                "input_cost": cost.get("input_cost", 0),
                "output_cost": cost.get("output_cost", 0),
                "total_cost": cost.get("total_cost", 0)
            })
        
        return {
            "models": models,
            "usage_counts": usage_counts,
            "token_data": token_data,
            "cost_data": cost_data
        }
    
    def _format_user_data(self, user_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format user data.
        
        Args:
            user_metrics: User metrics
            
        Returns:
            Formatted user data
        """
        browser_distribution = user_metrics.get("browser_distribution", {})
        os_distribution = user_metrics.get("os_distribution", {})
        hour_distribution = user_metrics.get("hour_distribution", {})
        
        # Format for charts
        browsers = list(browser_distribution.keys())
        browser_counts = list(browser_distribution.values())
        
        os_names = list(os_distribution.keys())
        os_counts = list(os_distribution.values())
        
        # Format hour distribution
        hours = []
        hour_counts = []
        
        for hour in range(24):
            hours.append(str(hour))
            hour_counts.append(hour_distribution.get(hour, 0))
        
        # Format session duration
        session_duration = user_metrics.get("session_duration", {})
        duration_distribution = session_duration.get("distribution", [])
        
        return {
            "browsers": browsers,
            "browser_counts": browser_counts,
            "os_names": os_names,
            "os_counts": os_counts,
            "hours": hours,
            "hour_counts": hour_counts,
            "avg_session_duration": session_duration.get("avg", 0),
            "median_session_duration": session_duration.get("median", 0),
            "duration_distribution": duration_distribution
        }
    
    def _format_performance_data(self, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format performance data.
        
        Args:
            performance_metrics: Performance metrics
            
        Returns:
            Formatted performance data
        """
        processing_time = performance_metrics.get("processing_time", {})
        token_usage = performance_metrics.get("token_usage", [])
        
        # Format processing time distribution
        distribution = processing_time.get("distribution", [])
        
        # Format token usage over time
        dates = []
        prompt_tokens = []
        completion_tokens = []
        total_tokens = []
        
        for day in token_usage:
            dates.append(day.get("date", ""))
            prompt_tokens.append(day.get("prompt_tokens", 0))
            completion_tokens.append(day.get("completion_tokens", 0))
            total_tokens.append(day.get("total_tokens", 0))
        
        return {
            "avg_processing_time": processing_time.get("avg", 0),
            "median_processing_time": processing_time.get("median", 0),
            "p90_processing_time": processing_time.get("p90", 0),
            "p95_processing_time": processing_time.get("p95", 0),
            "p99_processing_time": processing_time.get("p99", 0),
            "processing_time_distribution": distribution,
            "token_efficiency": performance_metrics.get("token_efficiency", 0),
            "dates": dates,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    
    def _generate_html(self, dashboard_data: Dict[str, Any]) -> str:
        """
        Generate HTML for the dashboard.
        
        Args:
            dashboard_data: Formatted dashboard data
            
        Returns:
            HTML string
        """
        # Load template
        template_path = os.path.join(os.path.dirname(__file__), "dashboard_template.html")
        
        if not os.path.exists(template_path):
            # Use default template if custom template doesn't exist
            template = self._get_default_template()
        else:
            with open(template_path, "r") as f:
                template = f.read()
        
        # Convert dashboard data to JSON
        dashboard_json = json.dumps(dashboard_data)
        
        # Replace placeholder with actual data
        html = template.replace("const DASHBOARD_DATA = {};", f"const DASHBOARD_DATA = {dashboard_json};")
        
        return html
    
    def _get_default_template(self) -> str:
        """
        Get default HTML template.
        
        Returns:
            Default HTML template
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MongoDB Monitoring Dashboard</title>
    
    <!-- Include Chart.js for charts -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        :root {
            --primary-color: #4a6fa5;
            --secondary-color: #6c757d;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
            --border-radius: 8px;
            --box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            
            --bg-color: #f5f7fa;
            --card-bg-color: #ffffff;
            --text-color: #333333;
            --border-color: #eeeeee;
            --content-box-bg: #f8f9fa;
            --hover-color: #e9ecef;
        }
        
        [data-theme="dark"] {
            --primary-color: #5a8dd6;
            --secondary-color: #adb5bd;
            --success-color: #48c774;
            --warning-color: #ffdd57;
            --danger-color: #f14668;
            
            --bg-color: #121212;
            --card-bg-color: #1e1e1e;
            --text-color: #e6e6e6;
            --border-color: #333333;
            --content-box-bg: #2d2d2d;
            --hover-color: #333333;
            --box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: var(--bg-color);
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        .dashboard-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        
        @media (min-width: 768px) {
            .dashboard-container {
                grid-template-columns: 1fr 1fr;
            }
        }
        
        .card {
            background: var(--card-bg-color);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 20px;
            margin-bottom: 20px;
            transition: background-color 0.3s ease;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .header h1 {
            margin: 0;
            color: var(--primary-color);
        }
        
        .metrics-summary {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .theme-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background-color: var(--card-bg-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            color: var(--text-color);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .theme-toggle:hover {
            background-color: var(--hover-color);
        }
        
        .metric-box {
            flex: 1;
            min-width: 150px;
            padding: 15px;
            border-radius: var(--border-radius);
            text-align: center;
            background: var(--card-bg-color);
            box-shadow: var(--box-shadow);
            transition: background-color 0.3s ease;
        }
        
        .metric-name {
            font-size: 14px;
            font-weight: 600;
            color: var(--secondary-color);
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .chart-container {
            height: 300px;
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>MongoDB Monitoring Dashboard</h1>
        <div>
            <button id="theme-toggle" class="theme-toggle">
                <span id="theme-icon">🌙</span>
                <span id="theme-text">Dark Mode</span>
            </button>
            <span id="timestamp"></span>
        </div>
    </div>
    
    <div class="dashboard-container">
        <!-- Summary Section -->
        <div class="card full-width">
            <h2>Summary</h2>
            <div class="metrics-summary" id="metrics-summary">
                <!-- Will be populated by JavaScript -->
            </div>
        </div>
        
        <!-- Usage Section -->
        <div class="card">
            <h2>Message Volume</h2>
            <div class="chart-container">
                <canvas id="message-volume-chart"></canvas>
            </div>
        </div>
        
        <!-- Token Usage Section -->
        <div class="card">
            <h2>Token Usage</h2>
            <div class="chart-container">
                <canvas id="token-usage-chart"></canvas>
            </div>
        </div>
        
        <!-- Processing Time Section -->
        <div class="card">
            <h2>Processing Time</h2>
            <div class="chart-container">
                <canvas id="processing-time-chart"></canvas>
            </div>
        </div>
        
        <!-- Model Usage Section -->
        <div class="card">
            <h2>Model Usage</h2>
            <div class="chart-container">
                <canvas id="model-usage-chart"></canvas>
            </div>
        </div>
        
        <!-- User Distribution Section -->
        <div class="card">
            <h2>Browser Distribution</h2>
            <div class="chart-container">
                <canvas id="browser-chart"></canvas>
            </div>
        </div>
        
        <!-- OS Distribution Section -->
        <div class="card">
            <h2>OS Distribution</h2>
            <div class="chart-container">
                <canvas id="os-chart"></canvas>
            </div>
        </div>
        
        <!-- Time of Day Section -->
        <div class="card">
            <h2>Time of Day Usage</h2>
            <div class="chart-container">
                <canvas id="time-of-day-chart"></canvas>
            </div>
        </div>
        
        <!-- Session Duration Section -->
        <div class="card">
            <h2>Session Duration</h2>
            <div class="chart-container">
                <canvas id="session-duration-chart"></canvas>
            </div>
        </div>
        
        <!-- Model Cost Section -->
        <div class="card full-width">
            <h2>Model Cost</h2>
            <div class="chart-container">
                <canvas id="model-cost-chart"></canvas>
            </div>
        </div>
    </div>
    
    <!-- Dashboard Data -->
    <script>
        const DASHBOARD_DATA = {};
    </script>
    
    <!-- Dashboard JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize the dashboard
            initializeDashboard(DASHBOARD_DATA);
            
            // Set up theme toggle
            const themeToggle = document.getElementById('theme-toggle');
            const themeIcon = document.getElementById('theme-icon');
            const themeText = document.getElementById('theme-text');
            
            themeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                
                if (currentTheme === 'dark') {
                    document.documentElement.removeAttribute('data-theme');
                    themeIcon.textContent = '🌙';
                    themeText.textContent = 'Dark Mode';
                } else {
                    document.documentElement.setAttribute('data-theme', 'dark');
                    themeIcon.textContent = '☀️';
                    themeText.textContent = 'Light Mode';
                }
                
                // Update charts for the new theme
                updateCharts();
            });
        });
        
        function initializeDashboard(data) {
            // Set timestamp
            if (data.timestamp) {
                document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleString();
            }
            
            // Render summary metrics
            renderSummaryMetrics(data.summary);
            
            // Render charts
            renderMessageVolumeChart(data.time_series);
            renderTokenUsageChart(data.time_series);
            renderProcessingTimeChart(data.time_series);
            renderModelUsageChart(data.model);
            renderBrowserChart(data.user);
            renderOSChart(data.user);
            renderTimeOfDayChart(data.user);
            renderSessionDurationChart(data.user);
            renderModelCostChart(data.model);
        }
        
        function renderSummaryMetrics(summary) {
            const container = document.getElementById('metrics-summary');
            container.innerHTML = '';
            
            // Define metrics to display
            const metrics = [
                { name: 'Total Sessions', value: summary.total_sessions },
                { name: 'Active Sessions', value: summary.active_sessions },
                { name: 'User Messages', value: summary.user_messages },
                { name: 'Assistant Messages', value: summary.assistant_messages },
                { name: 'Avg Processing Time (ms)', value: summary.avg_processing_time.toFixed(2) },
                { name: 'Token Efficiency', value: summary.token_efficiency.toFixed(2) },
                { name: 'Unique Users', value: summary.unique_users }
            ];
            
            // Create metric boxes
            metrics.forEach(metric => {
                const metricBox = document.createElement('div');
                metricBox.className = 'metric-box';
                
                const nameElement = document.createElement('div');
                nameElement.className = 'metric-name';
                nameElement.textContent = metric.name;
                
                const valueElement = document.createElement('div');
                valueElement.className = 'metric-value';
                valueElement.textContent = metric.value;
                
                metricBox.appendChild(nameElement);
                metricBox.appendChild(valueElement);
                
                container.appendChild(metricBox);
            });
        }
        
        function renderMessageVolumeChart(timeSeriesData) {
            const ctx = document.getElementById('message-volume-chart').getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timeSeriesData.dates,
                    datasets: [
                        {
                            label: 'User Messages',
                            data: timeSeriesData.user_messages,
                            borderColor: '#4a6fa5',
                            backgroundColor: 'rgba(74, 111, 165, 0.1)',
                            tension: 0.1,
                            fill: true
                        },
                        {
                            label: 'Assistant Messages',
                            data: timeSeriesData.assistant_messages,
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.1,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function renderTokenUsageChart(timeSeriesData) {
            const ctx = document.getElementById('token-usage-chart').getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timeSeriesData.dates,
                    datasets: [
                        {
                            label: 'Total Tokens',
                            data: timeSeriesData.total_tokens,
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.1,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function renderProcessingTimeChart(timeSeriesData) {
            const ctx = document.getElementById('processing-time-chart').getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timeSeriesData.dates,
                    datasets: [
                        {
                            label: 'Avg Processing Time (ms)',
                            data: timeSeriesData.processing_times,
                            borderColor: '#ffc107',
                            backgroundColor: 'rgba(255, 193, 7, 0.1)',
                            tension: 0.1,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function renderModelUsageChart(modelData) {
            const ctx = document.getElementById('model-usage-chart').getContext('2d');
            
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: modelData.models,
                    datasets: [
                        {
                            data: modelData.usage_counts,
                            backgroundColor: [
                                '#4a6fa5',
                                '#28a745',
                                '#dc3545',
                                '#ffc107',
                                '#6c757d',
                                '#17a2b8'
                            ]
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        function renderBrowserChart(userData) {
            const ctx = document.getElementById('browser-chart').getContext('2d');
            
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: userData.browsers,
                    datasets: [
                        {
                            data: userData.browser_counts,
                            backgroundColor: [
                                '#4a6fa5',
                                '#28a745',
                                '#dc3545',
                                '#ffc107',
                                '#6c757d',
                                '#17a2b8'
                            ]
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        function renderOSChart(userData) {
            const ctx = document.getElementById('os-chart').getContext('2d');
            
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: userData.os_names,
                    datasets: [
                        {
                            data: userData.os_counts,
                            backgroundColor: [
                                '#4a6fa5',
                                '#28a745',
                                '#dc3545',
                                '#ffc107',
                                '#6c757d',
                                '#17a2b8'
                            ]
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        function renderTimeOfDayChart(userData) {
            const ctx = document.getElementById('time-of-day-chart').getContext('2d');
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: userData.hours,
                    datasets: [
                        {
                            label: 'Sessions',
                            data: userData.hour_counts,
                            backgroundColor: 'rgba(74, 111, 165, 0.7)',
                            borderColor: 'rgba(74, 111, 165, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function renderSessionDurationChart(userData) {
            const ctx = document.getElementById('session-duration-chart').getContext('2d');
            
            // Create labels for bins
            const labels = [];
            for (let i = 0; i < userData.duration_distribution.length; i++) {
                labels.push(`Bin ${i+1}`);
            }
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Session Count',
                            data: userData.duration_distribution,
                            backgroundColor: 'rgba(40, 167, 69, 0.7)',
                            borderColor: 'rgba(40, 167, 69, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function renderModelCostChart(modelData) {
            const ctx = document.getElementById('model-cost-chart').getContext('2d');
            
            // Extract data for chart
            const models = [];
            const inputCosts = [];
            const outputCosts = [];
            
            modelData.cost_data.forEach(item => {
                models.push(item.model);
                inputCosts.push(item.input_cost);
                outputCosts.push(item.output_cost);
            });
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: models,
                    datasets: [
                        {
                            label: 'Input Cost ($)',
                            data: inputCosts,
                            backgroundColor: 'rgba(74, 111, 165, 0.7)',
                            borderColor: 'rgba(74, 111, 165, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Output Cost ($)',
                            data: outputCosts,
                            backgroundColor: 'rgba(220, 53, 69, 0.7)',
                            borderColor: 'rgba(220, 53, 69, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function updateCharts() {
            // Force redraw all charts with new theme colors
            Chart.instances.forEach(chart => {
                chart.update();
            });
        }
    </script>
</body>
</html>
"""
