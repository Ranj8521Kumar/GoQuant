"""
Performance measurement utilities.
"""
import time
import numpy as np
from typing import List, Dict, Any, Optional
from functools import wraps

class PerformanceTracker:
    """Track performance metrics for different operations."""
    
    def __init__(self, max_samples: int = 1000):
        """
        Initialize performance tracker.
        
        Args:
            max_samples: Maximum number of samples to keep for each metric
        """
        self.max_samples = max_samples
        self.metrics = {}
    
    def record(self, metric_name: str, value: float):
        """
        Record a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Value to record (typically time in seconds)
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append(value)
        
        # Keep only the last max_samples
        if len(self.metrics[metric_name]) > self.max_samples:
            self.metrics[metric_name].pop(0)
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """
        Get statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Dictionary with statistics (mean, median, min, max, p95, p99)
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {
                'mean': 0,
                'median': 0,
                'min': 0,
                'max': 0,
                'p95': 0,
                'p99': 0,
                'count': 0
            }
        
        values = np.array(self.metrics[metric_name])
        return {
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'p95': float(np.percentile(values, 95)),
            'p99': float(np.percentile(values, 99)),
            'count': len(values)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for all metrics.
        
        Returns:
            Dictionary with statistics for each metric
        """
        return {metric: self.get_stats(metric) for metric in self.metrics}
    
    def reset(self, metric_name: Optional[str] = None):
        """
        Reset metrics.
        
        Args:
            metric_name: Name of the metric to reset, or None to reset all
        """
        if metric_name is None:
            self.metrics = {}
        elif metric_name in self.metrics:
            self.metrics[metric_name] = []


def timeit(tracker: PerformanceTracker, metric_name: str):
    """
    Decorator to measure execution time of a function.
    
    Args:
        tracker: PerformanceTracker instance
        metric_name: Name of the metric to record
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            tracker.record(metric_name, execution_time)
            return result
        return wrapper
    return decorator


# Global performance tracker instance
performance_tracker = PerformanceTracker()
