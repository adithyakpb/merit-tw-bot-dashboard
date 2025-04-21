from typing import Dict, Any, List, Optional
from merit.api.gemini_client import GeminiClient

class InsightsGenerator:
    """
    Generates insights from metrics using GeminiClient.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the insights generator.
        
        Args:
            api_key: GeminiClient API key
        """
        self.client = GeminiClient(api_key=api_key)
        
    def generate_insights(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from metrics.
        
        Args:
            metrics: Calculated metrics
            
        Returns:
            Dictionary of insights
        """
        # Format metrics for the prompt
        metrics_text = self._format_metrics_for_prompt(metrics)
        
        # Generate insights using GeminiClient
        prompt = f"""
        You are an analytics expert analyzing chat system metrics. Based on the following metrics, 
        provide 3-5 key insights about system performance, user behavior, and potential improvements.
        
        Metrics:
        {metrics_text}
        
        For each insight:
        1. Provide a clear, concise title
        2. Explain the insight with specific data points
        3. Suggest actionable recommendations based on the insight
        
        Format your response as a structured list with clear headings and bullet points.
        """
        
        insights_text = self.client.generate_text(prompt)
        
        return {
            "text": insights_text,
            "metrics": metrics
        }
    
    def generate_anomaly_detection(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate anomaly detection insights.
        
        Args:
            metrics: Calculated metrics
            
        Returns:
            Dictionary of anomaly detection insights
        """
        # Format metrics for the prompt
        metrics_text = self._format_metrics_for_prompt(metrics)
        
        # Generate anomaly detection using GeminiClient
        prompt = f"""
        You are an AI monitoring expert. Analyze the following metrics from a chat system and identify
        any anomalies or unusual patterns that might indicate issues or opportunities.
        
        Metrics:
        {metrics_text}
        
        For each anomaly:
        1. Describe the anomaly clearly
        2. Explain why it's unusual or concerning
        3. Suggest possible causes
        4. Recommend actions to investigate or address it
        
        Focus on metrics that show significant deviations from normal patterns, unexpected spikes or drops,
        or values that are outside of acceptable thresholds.
        
        Format your response as a structured list with clear headings and bullet points.
        """
        
        anomaly_text = self.client.generate_text(prompt)
        
        return {
            "text": anomaly_text,
            "metrics": metrics
        }
    
    def generate_recommendations(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recommendations for system improvements.
        
        Args:
            metrics: Calculated metrics
            
        Returns:
            Dictionary of recommendations
        """
        # Format metrics for the prompt
        metrics_text = self._format_metrics_for_prompt(metrics)
        
        # Generate recommendations using GeminiClient
        prompt = f"""
        You are a chat system optimization expert. Based on the following metrics, provide
        specific recommendations to improve system performance, user experience, and cost efficiency.
        
        Metrics:
        {metrics_text}
        
        For each recommendation:
        1. Provide a clear, actionable title
        2. Explain the rationale behind the recommendation with specific data points
        3. Describe the expected benefits
        4. Suggest implementation steps
        
        Focus on practical recommendations that would have the most significant impact.
        
        Format your response as a structured list with clear headings and bullet points.
        """
        
        recommendations_text = self.client.generate_text(prompt)
        
        return {
            "text": recommendations_text,
            "metrics": metrics
        }
    
    def _format_metrics_for_prompt(self, metrics: Dict[str, Any]) -> str:
        """
        Format metrics for the prompt.
        
        Args:
            metrics: Calculated metrics
            
        Returns:
            Formatted metrics text
        """
        # Extract key metrics
        usage = metrics.get("usage", {})
        performance = metrics.get("performance", {})
        model = metrics.get("model", {})
        user = metrics.get("user", {})
        
        # Format usage metrics
        usage_text = f"""
        Usage Metrics:
        - Total Sessions: {usage.get("total_sessions", 0)}
        - Active Sessions: {usage.get("active_sessions", 0)}
        - Completed Sessions: {usage.get("completed_sessions", 0)}
        - User Messages: {usage.get("user_messages", 0)}
        - Assistant Messages: {usage.get("assistant_messages", 0)}
        - User/Assistant Message Ratio: {usage.get("message_ratio", 0):.2f}
        - Messages per Session: Avg {usage.get("messages_per_session", {}).get("avg", 0):.2f}, Min {usage.get("messages_per_session", {}).get("min", 0)}, Max {usage.get("messages_per_session", {}).get("max", 0)}
        """
        
        # Format performance metrics
        processing_time = performance.get("processing_time", {})
        performance_text = f"""
        Performance Metrics:
        - Avg Processing Time: {processing_time.get("avg", 0):.2f} ms
        - Median Processing Time: {processing_time.get("median", 0):.2f} ms
        - P90 Processing Time: {processing_time.get("p90", 0):.2f} ms
        - P95 Processing Time: {processing_time.get("p95", 0):.2f} ms
        - P99 Processing Time: {processing_time.get("p99", 0):.2f} ms
        - Token Efficiency (output/input): {performance.get("token_efficiency", 0):.2f}
        """
        
        # Format model metrics
        model_usage = model.get("model_usage", {})
        model_text = f"""
        Model Metrics:
        - Model Usage: {', '.join([f"{model}: {count}" for model, count in model_usage.items()])}
        """
        
        # Format user metrics
        user_text = f"""
        User Metrics:
        - Unique Users: {user.get("unique_users", 0)}
        - Avg Session Duration: {user.get("session_duration", {}).get("avg", 0):.2f} seconds
        - Median Session Duration: {user.get("session_duration", {}).get("median", 0):.2f} seconds
        - Browser Distribution: {', '.join([f"{browser}: {count}" for browser, count in user.get("browser_distribution", {}).items()])}
        - OS Distribution: {', '.join([f"{os}: {count}" for os, count in user.get("os_distribution", {}).items()])}
        """
        
        # Combine all metrics
        return f"{usage_text}\n{performance_text}\n{model_text}\n{user_text}"
