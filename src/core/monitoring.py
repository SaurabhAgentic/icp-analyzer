from prometheus_client import Counter, Histogram, Gauge, start_http_server
from prometheus_client.exposition import MetricsHandler
from prometheus_client.registry import CollectorRegistry
from prometheus_client.multiprocess import MultiProcessCollector
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from typing import Dict, Any, Optional
import os
import time
from functools import wraps
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Monitoring:
    def __init__(self):
        """Initialize monitoring components."""
        # Initialize Prometheus metrics
        self.registry = CollectorRegistry()
        MultiProcessCollector(self.registry)
        
        # Request metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_latency = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Analysis metrics
        self.analysis_count = Counter(
            'analysis_requests_total',
            'Total number of analysis requests',
            ['analysis_type'],
            registry=self.registry
        )
        
        self.analysis_duration = Histogram(
            'analysis_duration_seconds',
            'Analysis duration in seconds',
            ['analysis_type'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total number of cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total number of cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_operation_duration = Histogram(
            'db_operation_duration_seconds',
            'Database operation duration in seconds',
            ['operation', 'collection'],
            registry=self.registry
        )
        
        self.db_errors = Counter(
            'db_errors_total',
            'Total number of database errors',
            ['operation', 'collection'],
            registry=self.registry
        )
        
        # System metrics
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Current memory usage in bytes',
            registry=self.registry
        )
        
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'Current CPU usage percentage',
            registry=self.registry
        )
        
        # Initialize Sentry
        sentry_dsn = os.getenv('SENTRY_DSN')
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0,
                environment=os.getenv('FLASK_ENV', 'development')
            )
        
        # Start Prometheus metrics server
        metrics_port = int(os.getenv('METRICS_PORT', 9090))
        start_http_server(metrics_port, registry=self.registry)
        logger.info(f"Started Prometheus metrics server on port {metrics_port}")
    
    def track_request(self, method: str, endpoint: str, status: int):
        """Track HTTP request metrics."""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
    
    def track_request_latency(self, method: str, endpoint: str, duration: float):
        """Track HTTP request latency."""
        self.request_latency.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def track_analysis(self, analysis_type: str, duration: float):
        """Track analysis metrics."""
        self.analysis_count.labels(analysis_type=analysis_type).inc()
        self.analysis_duration.labels(analysis_type=analysis_type).observe(duration)
    
    def track_cache(self, cache_type: str, hit: bool):
        """Track cache metrics."""
        if hit:
            self.cache_hits.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses.labels(cache_type=cache_type).inc()
    
    def track_db_operation(self, operation: str, collection: str, duration: float):
        """Track database operation metrics."""
        self.db_operation_duration.labels(
            operation=operation,
            collection=collection
        ).observe(duration)
    
    def track_db_error(self, operation: str, collection: str):
        """Track database error metrics."""
        self.db_errors.labels(
            operation=operation,
            collection=collection
        ).inc()
    
    def update_system_metrics(self, memory_bytes: int, cpu_percent: float):
        """Update system resource metrics."""
        self.memory_usage.set(memory_bytes)
        self.cpu_usage.set(cpu_percent)
    
    def track_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Track exceptions in Sentry."""
        if context:
            sentry_sdk.set_context('additional', context)
        sentry_sdk.capture_exception(exception)
    
    def track_event(self, event_name: str, data: Optional[Dict[str, Any]] = None):
        """Track custom events in Sentry."""
        if data:
            sentry_sdk.set_context('event_data', data)
        sentry_sdk.capture_message(event_name)

def track_operation(operation_type: str):
    """Decorator for tracking operation duration and errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitoring.track_analysis(operation_type, duration)
                return result
            except Exception as e:
                monitoring.track_exception(e, {
                    'operation_type': operation_type,
                    'args': str(args),
                    'kwargs': str(kwargs)
                })
                raise
        return wrapper
    return decorator

# Initialize global monitoring instance
monitoring = Monitoring() 