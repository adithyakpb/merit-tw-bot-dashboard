#!/usr/bin/env python3
"""
MongoDB Monitoring Dashboard

This script creates a monitoring dashboard for MongoDB logs using MERIT AI.
It connects to a MongoDB database, extracts log data, calculates metrics,
and generates a dashboard with visualizations and AI-powered insights.
"""

import os
import argparse
from datetime import datetime

from merit.api.gemini_client import GeminiClient

from mongodb_collector import MongoDBCollector
from metrics_processor import MetricsProcessor
from dashboard_generator import DashboardGenerator
from insights_generator import InsightsGenerator

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MongoDB Monitoring Dashboard")
    
    parser.add_argument("--connection", type=str, default="mongodb://localhost:27017/",
                        help="MongoDB connection string")
    parser.add_argument("--database", type=str, default="chat_logs",
                        help="MongoDB database name")
    parser.add_argument("--session-collection", type=str, default="Session",
                        help="MongoDB session collection name")
    parser.add_argument("--message-collection", type=str, default="MessageLog",
                        help="MongoDB message collection name")
    parser.add_argument("--output", type=str, default="mongodb_dashboard.html",
                        help="Output path for the dashboard HTML")
    parser.add_argument("--api-key", type=str,
                        default=os.getenv("GOOGLE_API_KEY", "AIzaSyBlI7KwsmbYklgXcMuAdhjx7MHb6kncTSE"),
                        help="Google API key for GeminiClient")
    parser.add_argument("--time-range", type=int, default=24,
                        help="Time range in hours to query (default: 24)")
    parser.add_argument("--batch-size", type=int, default=1000,
                        help="Number of documents to process at once (default: 1000)")
    parser.add_argument("--insights", action="store_true",
                        help="Generate AI insights using GeminiClient")
    parser.add_argument("--insights-file", type=str, default="mongodb_insights.txt",
                        help="Output path for the insights text file")
    
    return parser.parse_args()

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    print(f"[{datetime.now()}] Starting MongoDB Monitoring Dashboard")
    
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
    dashboard = DashboardGenerator(processor)
    
    # Start collector
    print(f"[{datetime.now()}] Starting collector")
    collector.start()
    
    try:
        # Generate dashboard
        print(f"[{datetime.now()}] Generating dashboard")
        dashboard_path = dashboard.generate_dashboard(output_path=args.output)
        print(f"[{datetime.now()}] Dashboard generated at: {dashboard_path}")
        
        # Generate insights if requested
        if args.insights:
            print(f"[{datetime.now()}] Generating insights")
            insights = InsightsGenerator(args.api_key)
            
            # Calculate metrics
            metrics = processor.calculate_metrics()
            
            # Generate insights
            insights_data = insights.generate_insights(metrics)
            
            # Save insights to file
            with open(args.insights_file, "w") as f:
                f.write(insights_data["text"])
            
            print(f"[{datetime.now()}] Insights generated at: {args.insights_file}")
            
            # Generate anomaly detection
            anomaly_data = insights.generate_anomaly_detection(metrics)
            
            # Save anomaly detection to file
            anomaly_file = args.insights_file.replace(".txt", "_anomalies.txt")
            with open(anomaly_file, "w") as f:
                f.write(anomaly_data["text"])
            
            print(f"[{datetime.now()}] Anomaly detection generated at: {anomaly_file}")
            
            # Generate recommendations
            recommendations_data = insights.generate_recommendations(metrics)
            
            # Save recommendations to file
            recommendations_file = args.insights_file.replace(".txt", "_recommendations.txt")
            with open(recommendations_file, "w") as f:
                f.write(recommendations_data["text"])
            
            print(f"[{datetime.now()}] Recommendations generated at: {recommendations_file}")
    
    finally:
        # Stop collector
        print(f"[{datetime.now()}] Stopping collector")
        collector.stop()
    
    print(f"[{datetime.now()}] MongoDB Monitoring Dashboard completed")

if __name__ == "__main__":
    main()
