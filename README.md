# MongoDB Monitoring Dashboard

A comprehensive monitoring dashboard for MongoDB chat logs using MERIT AI.

## Overview

This project creates a monitoring dashboard for MongoDB logs, specifically designed for chat applications. It connects to a MongoDB database, extracts log data, calculates various metrics, and generates an interactive HTML dashboard with visualizations. It also provides AI-powered insights using the GeminiClient.

The project offers two dashboard options:
1. **Static Dashboard**: Generates a one-time HTML dashboard
2. **Live Dashboard**: Provides a real-time updating dashboard with WebSocket support

## Setup Instructions

1. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MongoDB connection**:
   Ensure your MongoDB server is running. The default connection is `mongodb://localhost:27017/`.

## Running the Dashboard

### Option 1: Static Dashboard

Generate a one-time HTML dashboard:

```bash
python mongodb_dashboard.py --connection "mongodb://localhost:27017/" --database "your_database" --session-collection "your_session_collection" --message-collection "your_message_collection"
```

This will create `mongodb_dashboard.html` which you can open in any browser.

### Option 2: Live Dashboard (Recommended)

Start the live dashboard server with real-time updates:

```bash
python dashboard_server.py --connection "mongodb://localhost:27017/" --database "your_database" --session-collection "your_session_collection" --message-collection "your_message_collection" --port 5502
```

Then open your browser and navigate to: http://localhost:5502

## Command-line Arguments

### Static Dashboard Command-line Arguments

- `--connection`: MongoDB connection string (default: "mongodb://localhost:27017/")
- `--database`: MongoDB database name (required)
- `--session-collection`: MongoDB session collection name (required)
- `--message-collection`: MongoDB message collection name (required)
- `--output`: Output path for the dashboard HTML (default: "mongodb_dashboard.html")
- `--api-key`: Google API key for GeminiClient (default: environment variable GOOGLE_API_KEY)
- `--time-range`: Time range in hours to query (default: 24)
- `--batch-size`: Number of documents to process at once (default: 1000)
- `--insights`: Generate AI insights using GeminiClient (flag)
- `--insights-file`: Output path for the insights text file (default: "mongodb_insights.txt")

### Live Dashboard Command-line Arguments

- `--connection`: MongoDB connection string (default: "mongodb://localhost:27017/")
- `--database`: MongoDB database name (required)
- `--session-collection`: MongoDB session collection name (required)
- `--message-collection`: MongoDB message collection name (required)
- `--time-range`: Time range in hours to query (default: 24)
- `--batch-size`: Number of documents to process at once (default: 100)
- `--update-interval`: Update interval in seconds (default: 10)
- `--host`: Host to bind the server to (default: "0.0.0.0")
- `--port`: Port to bind the server to (default: 5000)
- `--time-scale`: Initial time scale (minute, hour, day) (default: day)

## Example for Your Database

Based on your current setup:

```bash
python dashboard_server.py --connection "mongodb://localhost:27017/" --database "tw_gids_db" --session-collection "sessions" --message-collection "messagelogs" --port 5502
```

## Dashboard Features

- **MongoDB Integration**: Connects to MongoDB and extracts data from Session and MessageLog collections
- **Time Scale Controls**: Switch between minute, hour, and day views
- **Theme Toggle**: Switch between light and dark themes
- **Real-time Updates**: Data refreshes automatically every 10 seconds
- **Comprehensive Metrics**: Calculates usage, performance, model, and user metrics
- **Interactive Dashboard**: Generates an HTML dashboard with charts and visualizations
- **AI-Powered Insights**: Uses GeminiClient to generate insights, anomaly detection, and recommendations
- **Customizable**: Configurable through command-line arguments

## Metrics

The dashboard provides the following metrics:

### Usage Metrics
- Total sessions (daily/weekly/monthly)
- Active vs. completed sessions
- Messages per session (avg/min/max)
- User vs. assistant message ratio

### Performance Metrics
- Processing time (avg/median/p90/p95/p99)
- Token usage over time
- Token efficiency (output tokens / input tokens)

### Model Metrics
- Model usage distribution
- Token consumption by model
- Cost estimation by model

### User Metrics
- Unique users count
- Geographic distribution (based on IP addresses)
- Browser/OS distribution
- Session duration distribution
- Time-of-day usage patterns

## Generating AI Insights

To generate AI-powered insights (requires Google API key):

```bash
python mongodb_dashboard.py --connection "mongodb://localhost:27017/" --database "your_database" --session-collection "your_session_collection" --message-collection "your_message_collection" --insights --api-key "YOUR_GOOGLE_API_KEY"
```

This will generate three files:
- `mongodb_insights.txt`: General insights
- `mongodb_insights_anomalies.txt`: Anomaly detection
- `mongodb_insights_recommendations.txt`: Recommendations for improvement

## MongoDB Schema

The dashboard is designed to work with the following MongoDB schema:

### Session Collection
```
{
  startTime: Date,              // When the session started
  endTime: Date,                // When the session ended (if completed)
  userIdentifier: String,       // User identifier
  totalMessages: Number,        // Count of messages in the session
  totalTokensUsed: Number,      // Total tokens consumed in the session
  active: Boolean,              // Whether the session is still active
  metadata: {                   // Session metadata
    userAgent: String,          // Browser/client information
    ipAddress: String,          // User's IP address
    browser: String,            // Browser type
    os: String                  // Operating system
  }
}
```

### MessageLog Collection
```
{
  sessionId: String,            // Reference to the parent session
  timestamp: Date,              // When the message was sent
  role: String,                 // Either 'user' or 'assistant'
  content: String,              // The actual message content
  model: String,                // The LLM model used
  tokensUsed: {                 // Token usage metrics
    prompt: Number,             // Tokens in the prompt
    completion: Number,         // Tokens in the completion (for assistant messages)
    total: Number               // Total tokens used
  },
  processingTime: Number,       // Time taken to process (in ms)
  metadata: {                   // Message metadata
    userAgent: String,          // Browser/client information
    ipAddress: String,          // User's IP address
    settings: Mixed             // Any model settings used (temperature, etc.)
  }
}
```

## Components

### Static Dashboard Components

The static dashboard consists of the following components:

1. **MongoDBCollector**: Connects to MongoDB and extracts data
2. **MetricsProcessor**: Calculates metrics from the collected data
3. **DashboardGenerator**: Generates the HTML dashboard
4. **InsightsGenerator**: Generates AI-powered insights using GeminiClient

### Live Dashboard Components

The live dashboard consists of the following components:

1. **MongoDBCollector**: Connects to MongoDB and extracts data
2. **MetricsProcessor**: Calculates metrics from the collected data
3. **Flask Web Server**: Serves the dashboard HTML and handles WebSocket connections
4. **Socket.IO**: Provides real-time communication between server and client
5. **Background Metrics Collector**: Periodically collects metrics and emits updates to clients
6. **Chart.js**: Renders interactive charts on the client side

## License

MIT
