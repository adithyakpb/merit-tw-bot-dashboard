#!/usr/bin/env python3
"""
MongoDB Live Monitoring Dashboard Server

This script creates a web server that serves a live monitoring dashboard for MongoDB logs.
It uses Flask for the web server and Socket.IO for real-time updates.
"""

import os
import argparse
import threading
import time
import json
from datetime import datetime, timedelta

from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO

from mongodb_collector import MongoDBCollector
from metrics_processor import MetricsProcessor

# Initialize Flask app and Socket.IO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
collector = None
processor = None
update_interval = 10  # seconds
is_running = False
time_scale = "day"  # Default time scale: day, hour, minute

@app.route('/')
def index():
    """Serve the dashboard HTML."""
    return render_template('dashboard.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

@socketio.on('set_time_scale')
def handle_time_scale(data):
    """Handle time scale change from client."""
    global time_scale
    new_scale = data.get('scale')
    if new_scale in ['minute', 'hour', 'day']:
        time_scale = new_scale
        print(f"[{datetime.now()}] Time scale changed to: {time_scale}")
        
        # Recalculate metrics with new time scale
        metrics = processor.calculate_metrics()
        dashboard_data = format_dashboard_data(metrics)
        socketio.emit('metrics_update', dashboard_data)

def format_dashboard_data(metrics):
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
    
    # Format time series data based on time scale
    if time_scale == "day":
        time_series = format_daily_time_series(usage.get("daily", []))
    elif time_scale == "hour":
        time_series = format_hourly_time_series(usage.get("hourly", []))
    else:  # minute
        time_series = format_minute_time_series(usage.get("minute", []))
    
    # Format model data
    model_data = format_model_data(model)
    
    # Format user data
    user_data = format_user_data(user)
    
    # Format performance data
    performance_data = format_performance_data(performance)
    
    # Combine all data
    return {
        "summary": summary,
        "time_series": time_series,
        "model": model_data,
        "user": user_data,
        "performance": performance_data,
        "timestamp": datetime.now().isoformat(),
        "time_scale": time_scale
    }

def format_daily_time_series(daily_data):
    """Format daily time series data."""
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
        "processing_times": processing_times,
        "scale": "day"
    }

def format_hourly_time_series(hourly_data):
    """Format hourly time series data."""
    dates = []
    user_messages = []
    assistant_messages = []
    total_tokens = []
    processing_times = []
    
    for hour in hourly_data:
        dates.append(hour.get("hour", ""))
        
        messages = hour.get("messages", {})
        user_messages.append(messages.get("user", 0))
        assistant_messages.append(messages.get("assistant", 0))
        
        total_tokens.append(hour.get("total_tokens", 0))
        processing_times.append(hour.get("avg_processing_time", 0))
    
    return {
        "dates": dates,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "total_tokens": total_tokens,
        "processing_times": processing_times,
        "scale": "hour"
    }

def format_minute_time_series(minute_data):
    """Format minute time series data."""
    dates = []
    user_messages = []
    assistant_messages = []
    total_tokens = []
    processing_times = []
    
    for minute in minute_data:
        dates.append(minute.get("minute", ""))
        
        messages = minute.get("messages", {})
        user_messages.append(messages.get("user", 0))
        assistant_messages.append(messages.get("assistant", 0))
        
        total_tokens.append(minute.get("total_tokens", 0))
        processing_times.append(minute.get("avg_processing_time", 0))
    
    return {
        "dates": dates,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "total_tokens": total_tokens,
        "processing_times": processing_times,
        "scale": "minute"
    }

def format_model_data(model_metrics):
    """Format model data."""
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

def format_user_data(user_metrics):
    """Format user data."""
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

def format_performance_data(performance_metrics):
    """Format performance data."""
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

def background_metrics_collector():
    """Background thread that collects metrics and emits to clients."""
    global is_running
    
    print(f"[{datetime.now()}] Starting background metrics collector")
    collector.start()
    
    try:
        while is_running:
            try:
                # Calculate metrics
                print(f"[{datetime.now()}] Collecting metrics")
                metrics = processor.calculate_metrics()
                
                # Format data for the dashboard
                dashboard_data = format_dashboard_data(metrics)
                
                # Emit to all clients
                print(f"[{datetime.now()}] Emitting metrics update")
                socketio.emit('metrics_update', dashboard_data)
                
                # Wait for next update
                time.sleep(update_interval)
            except Exception as e:
                print(f"[{datetime.now()}] Error collecting metrics: {str(e)}")
                time.sleep(update_interval)
    finally:
        collector.stop()
        print(f"[{datetime.now()}] Stopped background metrics collector")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MongoDB Live Monitoring Dashboard Server")
    
    parser.add_argument("--connection", type=str, default="mongodb://localhost:27017/",
                        help="MongoDB connection string")
    parser.add_argument("--database", type=str, default="chat_logs",
                        help="MongoDB database name")
    parser.add_argument("--session-collection", type=str, default="Session",
                        help="MongoDB session collection name")
    parser.add_argument("--message-collection", type=str, default="MessageLog",
                        help="MongoDB message collection name")
    parser.add_argument("--time-range", type=int, default=24,
                        help="Time range in hours to query (default: 24)")
    parser.add_argument("--batch-size", type=int, default=100,
                        help="Number of documents to process at once (default: 100)")
    parser.add_argument("--update-interval", type=int, default=10,
                        help="Update interval in seconds (default: 10)")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000,
                        help="Port to bind the server to (default: 5000)")
    parser.add_argument("--time-scale", type=str, choices=["minute", "hour", "day"], default="day",
                        help="Time scale for charts (default: day)")
    
    return parser.parse_args()

def main():
    """Main function."""
    global collector, processor, update_interval, is_running, time_scale
    
    # Parse command line arguments
    args = parse_args()
    update_interval = args.update_interval
    time_scale = args.time_scale
    
    print(f"[{datetime.now()}] Starting MongoDB Live Monitoring Dashboard Server")
    
    # MongoDB configuration
    mongodb_config = {
        "connection_string": args.connection,
        "database": args.database,
        "session_collection": args.session_collection,
        "message_collection": args.message_collection,
        "batch_size": args.batch_size,
        "time_range": args.time_range
    }
    
    # Initialize components
    print(f"[{datetime.now()}] Initializing components")
    collector = MongoDBCollector(mongodb_config)
    processor = MetricsProcessor(collector)
    
    # Start background thread
    is_running = True
    metrics_thread = threading.Thread(target=background_metrics_collector, daemon=True)
    metrics_thread.start()
    
    # Start Flask server
    try:
        print(f"[{datetime.now()}] Starting Flask server on {args.host}:{args.port}")
        socketio.run(app, host=args.host, port=args.port, debug=False, allow_unsafe_werkzeug=True)
    finally:
        # Stop background thread
        is_running = False
        metrics_thread.join(timeout=update_interval * 2)
        print(f"[{datetime.now()}] MongoDB Live Monitoring Dashboard Server stopped")

if __name__ == "__main__":
    main()
