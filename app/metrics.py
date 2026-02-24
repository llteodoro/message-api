"""Metrics and observability for the Message API."""

from threading import Lock
from typing import Dict
from collections import defaultdict
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class APIMetrics:
    """Thread-safe metrics collection for the API."""
    
    def __init__(self):
        """Initialize metrics."""
        self._lock = Lock()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.requests_by_type: Dict[str, int] = defaultdict(int)
        self.response_codes: Dict[str, int] = defaultdict(int)
        self.creation_attempts = 0
        self.successful_creations = 0
        self.failed_creations = 0
        self.start_time = datetime.now(timezone.utc)
    
    def record_request(self, method: str, status_code: int, success: bool):
        """
        Record a request.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            status_code: Response status code
            success: Whether the request was successful
        """
        with self._lock:
            self.total_requests += 1
            self.requests_by_type[method] += 1
            self.response_codes[str(status_code)] += 1
            
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
    
    def record_creation_attempt(self, success: bool):
        """
        Record a message creation attempt.
        
        Args:
            success: Whether the creation was successful
        """
        with self._lock:
            self.creation_attempts += 1
            if success:
                self.successful_creations += 1
            else:
                self.failed_creations += 1
    
    def get_metrics(self) -> dict:
        """
        Get all metrics.
        
        Returns:
            Dictionary of metrics
        """
        with self._lock:
            return {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "requests_by_type": dict(self.requests_by_type),
                "response_codes": dict(self.response_codes),
                "creation_attempts": self.creation_attempts,
                "successful_creations": self.successful_creations,
                "failed_creations": self.failed_creations,
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
            }
    
    def get_success_rate(self) -> float:
        """
        Calculate the success rate of all requests.
        
        Returns:
            Success rate as a percentage (0-100)
        """
        with self._lock:
            if self.total_requests == 0:
                return 0.0
            return (self.successful_requests / self.total_requests) * 100
    
    def get_creation_success_rate(self) -> float:
        """
        Calculate the success rate of message creation attempts.
        
        Returns:
            Success rate as a percentage (0-100)
        """
        with self._lock:
            if self.creation_attempts == 0:
                return 0.0
            return (self.successful_creations / self.creation_attempts) * 100
    
    def log_summary(self):
        """Log a summary of metrics."""
        metrics = self.get_metrics()
        logger.info(
            "Metrics Summary: "
            f"Total Requests={metrics['total_requests']}, "
            f"Successful={metrics['successful_requests']}, "
            f"Failed={metrics['failed_requests']}, "
            f"Success Rate={self.get_success_rate():.2f}%, "
            f"Message Creations={metrics['successful_creations']}/{metrics['creation_attempts']}"
        )
