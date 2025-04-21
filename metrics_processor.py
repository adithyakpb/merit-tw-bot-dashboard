from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import statistics

from mongodb_collector import MongoDBCollector

class MetricsProcessor:
    """
    Processes collected data to calculate monitoring metrics.
    """
    
    def __init__(self, collector: MongoDBCollector):
        """
        Initialize the metrics processor.
        
        Args:
            collector: The MongoDB collector to use
        """
        self.collector = collector
        
    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate all metrics from the collected data.
        
        Returns:
            Dictionary of calculated metrics
        """
        # Get sessions and messages
        sessions = self.collector.get_sessions(limit=1000)
        
        # Calculate metrics
        usage_metrics = self.calculate_usage_metrics(sessions)
        performance_metrics = self.calculate_performance_metrics()
        model_metrics = self.calculate_model_metrics()
        user_metrics = self.calculate_user_metrics(sessions)
        
        # Combine all metrics
        return {
            "usage": usage_metrics,
            "performance": performance_metrics,
            "model": model_metrics,
            "user": user_metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_usage_metrics(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate usage metrics.
        
        Args:
            sessions: List of session documents
            
        Returns:
            Dictionary of usage metrics
        """
        # Calculate basic session metrics
        total_sessions = len(sessions)
        active_sessions = sum(1 for s in sessions if s.get("active", False))
        completed_sessions = total_sessions - active_sessions
        
        # Calculate time-based metrics
        minute_metrics = self.collector.get_aggregated_metrics(group_by="minute")
        hourly_metrics = self.collector.get_aggregated_metrics(group_by="hour")
        daily_metrics = self.collector.get_aggregated_metrics(group_by="day")
        weekly_metrics = self.collector.get_aggregated_metrics(group_by="week")
        monthly_metrics = self.collector.get_aggregated_metrics(group_by="month")
        
        # Process time-based metrics
        minute_data = self._process_time_metrics(minute_metrics)
        hourly_data = self._process_time_metrics(hourly_metrics)
        daily_data = self._process_time_metrics(daily_metrics)
        weekly_data = self._process_time_metrics(weekly_metrics)
        monthly_data = self._process_time_metrics(monthly_metrics)
        
        # Calculate messages per session
        messages_per_session = []
        for session in sessions:
            session_id = session.get("_id")
            if session_id:
                messages = self.collector.get_messages_for_session(str(session_id))
                messages_per_session.append(len(messages))
        
        avg_messages_per_session = 0
        min_messages_per_session = 0
        max_messages_per_session = 0
        
        if messages_per_session:
            avg_messages_per_session = sum(messages_per_session) / len(messages_per_session)
            min_messages_per_session = min(messages_per_session)
            max_messages_per_session = max(messages_per_session)
        
        # Calculate user vs assistant message ratio
        user_messages = 0
        assistant_messages = 0
        
        for period in daily_data:
            for role, count in period.get("messages", {}).items():
                if role == "user":
                    user_messages += count
                elif role == "assistant":
                    assistant_messages += count
        
        message_ratio = 0
        if assistant_messages > 0:
            message_ratio = user_messages / assistant_messages
        
        # Combine metrics
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "active_ratio": active_sessions / total_sessions if total_sessions > 0 else 0,
            "messages_per_session": {
                "avg": avg_messages_per_session,
                "min": min_messages_per_session,
                "max": max_messages_per_session
            },
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "message_ratio": message_ratio,
            "minute": minute_data,
            "hourly": hourly_data,
            "daily": daily_data,
            "weekly": weekly_data,
            "monthly": monthly_data
        }
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """
        Calculate performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        # Get aggregated metrics
        daily_metrics = self.collector.get_aggregated_metrics(group_by="day")
        
        # Extract processing times
        processing_times = []
        
        # Get raw messages to calculate percentiles
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)  # Last 7 days
        
        query = {
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "role": "assistant"  # Only assistant messages have processing time
        }
        
        self.collector._messages.find(query)
        
        messages = list(self.collector._messages.find(query))
        
        for message in messages:
            processing_time = message.get("processingTime")
            if processing_time is not None:
                processing_times.append(processing_time)
        
        # Calculate processing time statistics
        avg_processing_time = 0
        median_processing_time = 0
        p90_processing_time = 0
        p95_processing_time = 0
        p99_processing_time = 0
        
        if processing_times:
            avg_processing_time = sum(processing_times) / len(processing_times)
            processing_times.sort()
            median_processing_time = statistics.median(processing_times)
            p90_processing_time = processing_times[int(len(processing_times) * 0.9)]
            p95_processing_time = processing_times[int(len(processing_times) * 0.95)]
            p99_processing_time = processing_times[int(len(processing_times) * 0.99)]
        
        # Calculate token usage over time
        token_usage = []
        
        for period_data in self._process_time_metrics(daily_metrics):
            token_usage.append({
                "date": period_data.get("date"),
                "prompt_tokens": period_data.get("prompt_tokens", 0),
                "completion_tokens": period_data.get("completion_tokens", 0),
                "total_tokens": period_data.get("total_tokens", 0)
            })
        
        # Calculate token efficiency
        total_prompt_tokens = sum(period.get("prompt_tokens", 0) for period in token_usage)
        total_completion_tokens = sum(period.get("completion_tokens", 0) for period in token_usage)
        
        token_efficiency = 0
        if total_prompt_tokens > 0:
            token_efficiency = total_completion_tokens / total_prompt_tokens
        
        # Calculate processing time distribution
        processing_time_distribution = self._calculate_distribution(processing_times, 10)
        
        # Combine metrics
        return {
            "processing_time": {
                "avg": avg_processing_time,
                "median": median_processing_time,
                "p90": p90_processing_time,
                "p95": p95_processing_time,
                "p99": p99_processing_time,
                "distribution": processing_time_distribution
            },
            "token_usage": token_usage,
            "token_efficiency": token_efficiency
        }
    
    def calculate_model_metrics(self) -> Dict[str, Any]:
        """
        Calculate model metrics.
        
        Returns:
            Dictionary of model metrics
        """
        # Get messages with model information
        query = {
            "model": {"$exists": True, "$ne": ""}
        }
        
        messages = list(self.collector._messages.find(query))
        
        # Calculate model usage
        model_usage = defaultdict(int)
        model_tokens = defaultdict(lambda: {"prompt": 0, "completion": 0, "total": 0})
        model_processing_times = defaultdict(list)
        
        for message in messages:
            model = message.get("model", "unknown")
            model_usage[model] += 1
            
            # Add token usage
            tokens = message.get("tokensUsed", {})
            model_tokens[model]["prompt"] += tokens.get("prompt", 0)
            model_tokens[model]["completion"] += tokens.get("completion", 0)
            model_tokens[model]["total"] += tokens.get("total", 0)
            
            # Add processing time
            processing_time = message.get("processingTime")
            if processing_time is not None:
                model_processing_times[model].append(processing_time)
        
        # Calculate average processing time per model
        model_avg_processing_time = {}
        
        for model, times in model_processing_times.items():
            if times:
                model_avg_processing_time[model] = sum(times) / len(times)
            else:
                model_avg_processing_time[model] = 0
        
        # Calculate cost estimation (simplified)
        model_cost = {}
        
        # Very simplified pricing - in a real implementation, use actual pricing data
        pricing = {
            "gpt-4": {"input": 0.00003, "output": 0.00006},
            "gpt-3.5-turbo": {"input": 0.0000015, "output": 0.000002},
            "claude-2": {"input": 0.00001, "output": 0.00003},
            "default": {"input": 0.000005, "output": 0.00001}
        }
        
        for model, tokens in model_tokens.items():
            # Get pricing for this model or use default
            model_pricing = pricing.get(model, pricing["default"])
            
            # Calculate cost
            input_cost = tokens["prompt"] * model_pricing["input"]
            output_cost = tokens["completion"] * model_pricing["output"]
            total_cost = input_cost + output_cost
            
            model_cost[model] = {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            }
        
        # Combine metrics
        return {
            "model_usage": dict(model_usage),
            "model_tokens": {model: dict(tokens) for model, tokens in model_tokens.items()},
            "model_processing_time": model_avg_processing_time,
            "model_cost": model_cost
        }
    
    def calculate_user_metrics(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate user metrics.
        
        Args:
            sessions: List of session documents
            
        Returns:
            Dictionary of user metrics
        """
        # Extract user identifiers
        user_ids = set()
        
        for session in sessions:
            user_id = session.get("userIdentifier")
            if user_id:
                user_ids.add(user_id)
        
        # Calculate geographic distribution
        geo_distribution = defaultdict(int)
        browser_distribution = defaultdict(int)
        os_distribution = defaultdict(int)
        
        for session in sessions:
            metadata = session.get("metadata", {})
            
            # Extract IP address for geo info (simplified)
            ip_address = metadata.get("ipAddress", "unknown")
            geo_distribution[ip_address] += 1
            
            # Extract browser and OS info
            browser = metadata.get("browser", "unknown")
            os = metadata.get("os", "unknown")
            
            browser_distribution[browser] += 1
            os_distribution[os] += 1
        
        # Calculate session duration
        session_durations = []
        
        for session in sessions:
            start_time = session.get("startTime")
            end_time = session.get("endTime")
            
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds()
                session_durations.append(duration)
        
        # Calculate session duration statistics
        avg_session_duration = 0
        median_session_duration = 0
        
        if session_durations:
            avg_session_duration = sum(session_durations) / len(session_durations)
            median_session_duration = statistics.median(session_durations)
        
        # Calculate session duration distribution
        session_duration_distribution = self._calculate_distribution(session_durations, 10)
        
        # Calculate time-of-day usage patterns
        hour_distribution = defaultdict(int)
        
        for session in sessions:
            start_time = session.get("startTime")
            
            if start_time:
                hour = start_time.hour
                hour_distribution[hour] += 1
        
        # Combine metrics
        return {
            "unique_users": len(user_ids),
            "geo_distribution": dict(geo_distribution),
            "browser_distribution": dict(browser_distribution),
            "os_distribution": dict(os_distribution),
            "session_duration": {
                "avg": avg_session_duration,
                "median": median_session_duration,
                "distribution": session_duration_distribution
            },
            "hour_distribution": dict(hour_distribution)
        }
    
    def _process_time_metrics(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process time-based metrics into a more usable format.
        
        Args:
            metrics: List of aggregated metrics
            
        Returns:
            List of processed metrics
        """
        # Group by time period
        period_data = defaultdict(lambda: {
            "messages": defaultdict(int),
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "avg_processing_time": 0
        })
        
        for metric in metrics:
            time_group = metric["_id"]["time_group"]
            role = metric["_id"]["role"]
            count = metric["count"]
            avg_processing_time = metric["avg_processing_time"] or 0
            prompt_tokens = metric["total_prompt_tokens"] or 0
            completion_tokens = metric["total_completion_tokens"] or 0
            total_tokens = metric["total_tokens"] or 0
            
            # Add to period data
            period_data[time_group]["messages"][role] += count
            period_data[time_group]["prompt_tokens"] += prompt_tokens
            period_data[time_group]["completion_tokens"] += completion_tokens
            period_data[time_group]["total_tokens"] += total_tokens
            
            # Only use assistant processing time
            if role == "assistant":
                period_data[time_group]["avg_processing_time"] = avg_processing_time
        
        # Convert to list
        result = []
        
        for time_group, data in period_data.items():
            result.append({
                "date": time_group,
                "messages": dict(data["messages"]),
                "prompt_tokens": data["prompt_tokens"],
                "completion_tokens": data["completion_tokens"],
                "total_tokens": data["total_tokens"],
                "avg_processing_time": data["avg_processing_time"]
            })
        
        # Sort by date
        result.sort(key=lambda x: x["date"])
        
        return result
    
    def _calculate_distribution(self, values: List[float], num_bins: int) -> List[int]:
        """
        Calculate distribution of values into bins.
        
        Args:
            values: List of values
            num_bins: Number of bins
            
        Returns:
            List of counts per bin
        """
        if not values:
            return [0] * num_bins
        
        # Calculate min and max
        min_value = min(values)
        max_value = max(values)
        
        # Handle case where all values are the same
        if min_value == max_value:
            result = [0] * num_bins
            result[0] = len(values)
            return result
        
        # Calculate bin size
        bin_size = (max_value - min_value) / num_bins
        
        # Initialize bins
        bins = [0] * num_bins
        
        # Count values in each bin
        for value in values:
            bin_index = min(int((value - min_value) / bin_size), num_bins - 1)
            bins[bin_index] += 1
        
        return bins
