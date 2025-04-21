from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from merit.monitoring.collectors.base import BaseDataCollector, CollectionResult, CollectionStatus
from merit.monitoring.models import LLMInteraction, LLMRequest, LLMResponse, TokenInfo

class MongoDBCollector(BaseDataCollector):
    """
    Collector that extracts data from MongoDB collections and converts to MERIT monitoring models.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MongoDB collector.
        
        Args:
            config: Configuration dictionary with the following options:
                - connection_string: MongoDB connection string
                - database: MongoDB database name
                - session_collection: Name of the session collection
                - message_collection: Name of the message log collection
                - batch_size: Number of documents to process at once
                - query_filter: Optional filter for MongoDB queries
                - time_range: Time range to query (in hours, default: 24)
        """
        super().__init__(config or {})
        self.connection_string = self.config.get("connection_string", "mongodb://localhost:27017/")
        self.database = self.config.get("database", "chat_logs")
        self.session_collection = self.config.get("session_collection", "Session")
        self.message_collection = self.config.get("message_collection", "MessageLog")
        self.batch_size = self.config.get("batch_size", 100)
        self.query_filter = self.config.get("query_filter", {})
        self.time_range = self.config.get("time_range", 24)  # in hours
        
        # Internal state
        self._client = None
        self._db = None
        self._sessions = None
        self._messages = None
        
    def start(self) -> None:
        """Start collecting data from MongoDB."""
        super().start()
        
        try:
            # Connect to MongoDB
            self._client = MongoClient(self.connection_string)
            self._db = self._client[self.database]
            self._sessions = self._db[self.session_collection]
            self._messages = self._db[self.message_collection]
            
            print(f"Connected to MongoDB: {self.database}")
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            self.is_running = False
    
    def stop(self) -> None:
        """Stop collecting data and close MongoDB connection."""
        super().stop()
        
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._sessions = None
            self._messages = None
    
    def collect(self) -> CollectionResult:
        """
        Collect data from MongoDB collections.
        
        Returns:
            CollectionResult with the extracted data
        """
        result = CollectionResult(
            status=CollectionStatus.SUCCESS,
            start_time=datetime.now()
        )
        
        if not self.is_running or not self._client:
            result.status = CollectionStatus.FAILURE
            result.error = "Collector not running or not connected to MongoDB"
            result.end_time = datetime.now()
            return result
        
        try:
            # Calculate time range for query
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=self.time_range)
            
            # Query messages within time range
            query = {
                "timestamp": {"$gte": start_time, "$lte": end_time}
            }
            query.update(self.query_filter)
            
            # Get messages
            messages = list(self._messages.find(query).limit(self.batch_size))
            result.items_processed = len(messages)
            
            # Process messages
            for message in messages:
                interaction = self._create_interaction(message)
                if interaction:
                    result.data.append(interaction)
                    result.items_collected += 1
                    
                    # Notify callbacks
                    self._notify_callbacks(interaction)
            
            # Determine final status
            if result.items_processed == 0:
                result.status = CollectionStatus.SUCCESS  # No data is still success
            elif result.items_collected == 0:
                result.status = CollectionStatus.FAILURE
                result.error = "No valid interactions found in MongoDB"
            elif result.items_collected < result.items_processed:
                result.status = CollectionStatus.PARTIAL
                result.error = f"Only processed {result.items_collected}/{result.items_processed} items"
        
        except Exception as e:
            result.status = CollectionStatus.FAILURE
            result.error = str(e)
        
        finally:
            result.end_time = datetime.now()
            return result
    
    def _create_interaction(self, message_doc: Dict[str, Any]) -> Optional[LLMInteraction]:
        """
        Convert MongoDB message document to LLMInteraction.
        
        Args:
            message_doc: MongoDB document from MessageLog collection
            
        Returns:
            LLMInteraction object or None if conversion not possible
        """
        try:
            # Extract basic information
            session_id = message_doc.get("sessionId")
            role = message_doc.get("role")
            content = message_doc.get("content", "")
            model = message_doc.get("model", "")
            timestamp = message_doc.get("timestamp", datetime.now())
            
            # Skip if missing essential data
            if not session_id or not role or not content:
                return None
            
            # Extract token usage
            tokens_data = message_doc.get("tokensUsed", {})
            prompt_tokens = tokens_data.get("prompt", 0)
            completion_tokens = tokens_data.get("completion", 0)
            total_tokens = tokens_data.get("total", prompt_tokens + completion_tokens)
            
            # Extract processing time
            processing_time = message_doc.get("processingTime", 0)
            
            # Extract metadata
            metadata = message_doc.get("metadata", {})
            
            # Create token info
            token_info = TokenInfo(
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
                total_tokens=total_tokens
            )
            
            # Create request and response based on role
            request_id = str(message_doc.get("_id", ""))
            
            if role == "user":
                # User message is a request
                request = LLMRequest(
                    id=request_id,
                    prompt=content,
                    model=model,
                    timestamp=timestamp,
                    metadata=metadata
                )
                
                # Create a minimal response
                response = LLMResponse(
                    request_id=request_id,
                    completion="",
                    model=model,
                    tokens=token_info,
                    latency=processing_time
                )
            else:
                # Assistant message is a response
                # We need to create a minimal request since we don't have the actual request
                request = LLMRequest(
                    id=request_id,
                    prompt="",
                    model=model,
                    timestamp=timestamp,
                    metadata=metadata
                )
                
                # Create the response
                response = LLMResponse(
                    request_id=request_id,
                    completion=content,
                    model=model,
                    tokens=token_info,
                    latency=processing_time
                )
            
            # Create the interaction
            return LLMInteraction(request=request, response=response)
            
        except Exception as e:
            print(f"Error creating interaction: {str(e)}")
            return None
    
    def get_sessions(self, limit: int = 100, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get sessions from MongoDB.
        
        Args:
            limit: Maximum number of sessions to return
            active_only: Whether to return only active sessions
            
        Returns:
            List of session documents
        """
        if not self.is_running or not self._client:
            return []
        
        try:
            query = {}
            if active_only:
                query["active"] = True
            
            return list(self._sessions.find(query).limit(limit))
        except Exception as e:
            print(f"Error getting sessions: {str(e)}")
            return []
    
    def get_messages_for_session(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get messages for a specific session.
        
        Args:
            session_id: Session ID to get messages for
            limit: Maximum number of messages to return
            
        Returns:
            List of message documents
        """
        if not self.is_running or not self._client:
            return []
        
        try:
            query = {"sessionId": session_id}
            return list(self._messages.find(query).limit(limit))
        except Exception as e:
            print(f"Error getting messages for session: {str(e)}")
            return []
    
    def get_aggregated_metrics(self, group_by: str = "day") -> List[Dict[str, Any]]:
        """
        Get aggregated metrics from MongoDB.
        
        Args:
            group_by: Time unit to group by ("minute", "hour", "day", "week", "month")
            
        Returns:
            List of aggregated metrics
        """
        if not self.is_running or not self._client:
            return []
        
        try:
            # Define time grouping
            time_format = "%Y-%m-%d"
            if group_by == "minute":
                time_format = "%Y-%m-%d %H:%M"
            elif group_by == "hour":
                time_format = "%Y-%m-%d %H:00"
            elif group_by == "week":
                time_format = "%Y-%U"
            elif group_by == "month":
                time_format = "%Y-%m"
            
            # Aggregation pipeline
            pipeline = [
                {
                    "$project": {
                        "time_group": {"$dateToString": {"format": time_format, "date": "$timestamp"}},
                        "role": 1,
                        "tokensUsed": 1,
                        "processingTime": 1,
                        "model": 1
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "time_group": "$time_group",
                            "role": "$role"
                        },
                        "count": {"$sum": 1},
                        "avg_processing_time": {"$avg": "$processingTime"},
                        "total_prompt_tokens": {"$sum": {"$ifNull": ["$tokensUsed.prompt", 0]}},
                        "total_completion_tokens": {"$sum": {"$ifNull": ["$tokensUsed.completion", 0]}},
                        "total_tokens": {"$sum": {"$ifNull": ["$tokensUsed.total", 0]}}
                    }
                },
                {
                    "$sort": {"_id.time_group": 1}
                }
            ]
            
            return list(self._messages.aggregate(pipeline))
        except Exception as e:
            print(f"Error getting aggregated metrics: {str(e)}")
            return []
