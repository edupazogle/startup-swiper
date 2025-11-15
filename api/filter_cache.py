"""
Caching and Rate Limiting for AXA Startup Filter

Provides:
1. LRU cache for LLM assessments
2. Rate limiting for API calls
3. Circuit breaker pattern
4. Retry logic with exponential backoff
"""

import time
import hashlib
import json
from typing import Any, Callable, Optional, Dict
from functools import wraps
from collections import OrderedDict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class LRUCache:
    """Simple LRU cache implementation"""
    
    def __init__(self, maxsize: int = 1000, ttl_seconds: int = 86400):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > self.ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, timestamp = self.cache[key]
        
        # Check expiration
        if self._is_expired(timestamp):
            del self.cache[key]
            self.misses += 1
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1
        return value
    
    def put(self, key: str, value: Any):
        """Put value in cache"""
        # Remove if exists
        if key in self.cache:
            del self.cache[key]
        
        # Add with timestamp
        self.cache[key] = (value, time.time())
        
        # Evict oldest if over limit
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'maxsize': self.maxsize,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }
    
    def __len__(self):
        return len(self.cache)
    
    def __contains__(self, key):
        return key in self.cache


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, calls: int, period: float):
        """
        Args:
            calls: Number of calls allowed per period
            period: Period in seconds
        """
        self.calls = calls
        self.period = period
        self.tokens = calls
        self.last_update = time.time()
        self.requests_made = 0
    
    def _refill(self):
        """Refill tokens based on time passed"""
        now = time.time()
        elapsed = now - self.last_update
        
        # Add tokens for time elapsed
        tokens_to_add = (elapsed / self.period) * self.calls
        self.tokens = min(self.calls, self.tokens + tokens_to_add)
        self.last_update = now
    
    def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens"""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            self.requests_made += 1
            return True
        
        return False
    
    def wait_time(self) -> float:
        """Get time to wait until next token available"""
        self._refill()
        
        if self.tokens >= 1:
            return 0.0
        
        tokens_needed = 1 - self.tokens
        return (tokens_needed / self.calls) * self.period
    
    def stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        self._refill()
        return {
            'tokens_available': self.tokens,
            'max_tokens': self.calls,
            'requests_made': self.requests_made,
            'wait_time': self.wait_time()
        }


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, fail_threshold: int = 5, timeout: float = 60):
        """
        Args:
            fail_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
        """
        self.fail_threshold = fail_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == 'open':
            # Check if we should try half-open
            if self.last_failure_time and \
               (time.time() - self.last_failure_time) > self.timeout:
                self.state = 'half_open'
                logger.info("Circuit breaker moving to half-open state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset or close circuit
            if self.state == 'half_open':
                self.state = 'closed'
                self.failure_count = 0
                logger.info("Circuit breaker closed after successful call")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(f"Circuit breaker failure {self.failure_count}/{self.fail_threshold}: {e}")
            
            # Open circuit if threshold reached
            if self.failure_count >= self.fail_threshold:
                self.state = 'open'
                logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
            
            raise
    
    def reset(self):
        """Reset circuit breaker"""
        self.state = 'closed'
        self.failure_count = 0
        self.last_failure_time = None
    
    def stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'fail_threshold': self.fail_threshold,
            'last_failure': self.last_failure_time
        }


def retry_with_backoff(max_attempts: int = 3, 
                       base_delay: float = 1.0,
                       backoff_factor: float = 2.0,
                       max_delay: float = 60.0):
    """Decorator for retry logic with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        # Last attempt, re-raise
                        logger.error(f"Final retry attempt failed: {e}")
                        raise
                    
                    # Calculate backoff delay
                    wait_time = min(delay, max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    delay *= backoff_factor
            
        return wrapper
    return decorator


class CachedLLMClient:
    """LLM client with caching, rate limiting, and circuit breaker"""
    
    def __init__(self, 
                 cache_ttl: int = 86400,
                 max_cache_size: int = 1000,
                 rate_limit_calls: int = 60,
                 rate_limit_period: float = 60.0,
                 circuit_breaker_threshold: int = 5,
                 circuit_breaker_timeout: float = 60.0):
        
        self.cache = LRUCache(maxsize=max_cache_size, ttl_seconds=cache_ttl)
        self.rate_limiter = RateLimiter(calls=rate_limit_calls, period=rate_limit_period)
        self.circuit_breaker = CircuitBreaker(
            fail_threshold=circuit_breaker_threshold,
            timeout=circuit_breaker_timeout
        )
    
    def _generate_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key from request parameters"""
        # Create deterministic key
        key_data = {
            'prompt': prompt,
            'model': model,
            **{k: v for k, v in sorted(kwargs.items())}
        }
        key_json = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_json.encode()).hexdigest()
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0, backoff_factor=2.0)
    def call_llm(self, 
                 llm_func: Callable,
                 prompt: str,
                 model: str,
                 use_cache: bool = True,
                 **kwargs) -> Any:
        """Call LLM with caching, rate limiting, and circuit breaker"""
        
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(prompt, model, **kwargs)
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for prompt hash: {cache_key[:8]}...")
                return cached_result
        
        # Rate limiting
        wait_time = self.rate_limiter.wait_time()
        if wait_time > 0:
            logger.info(f"Rate limit reached, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        if not self.rate_limiter.acquire():
            raise Exception("Rate limit exceeded")
        
        # Call LLM with circuit breaker
        def _make_call():
            return llm_func(prompt, model=model, **kwargs)
        
        result = self.circuit_breaker.call(_make_call)
        
        # Cache result
        if use_cache:
            self.cache.put(cache_key, result)
            logger.debug(f"Cached result for prompt hash: {cache_key[:8]}...")
        
        return result
    
    def stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            'cache': self.cache.stats(),
            'rate_limiter': self.rate_limiter.stats(),
            'circuit_breaker': self.circuit_breaker.stats()
        }
    
    def reset(self):
        """Reset all components"""
        self.cache.clear()
        self.circuit_breaker.reset()


# Global instance
_cached_client: Optional[CachedLLMClient] = None


def get_cached_llm_client(**kwargs) -> CachedLLMClient:
    """Get or create singleton cached LLM client"""
    global _cached_client
    
    if _cached_client is None:
        _cached_client = CachedLLMClient(**kwargs)
    
    return _cached_client


# Example usage
if __name__ == '__main__':
    # Test cache
    cache = LRUCache(maxsize=3, ttl_seconds=5)
    
    cache.put('key1', 'value1')
    cache.put('key2', 'value2')
    cache.put('key3', 'value3')
    
    print("Cache after 3 puts:", cache.stats())
    print("Get key1:", cache.get('key1'))
    print("Get key1 again:", cache.get('key1'))
    print("Get missing:", cache.get('key_missing'))
    print("Cache stats:", cache.stats())
    
    # Test rate limiter
    limiter = RateLimiter(calls=5, period=10.0)
    
    for i in range(7):
        if limiter.acquire():
            print(f"Request {i+1}: Allowed")
        else:
            print(f"Request {i+1}: Rate limited, wait {limiter.wait_time():.2f}s")
    
    print("Rate limiter stats:", limiter.stats())
    
    # Test circuit breaker
    breaker = CircuitBreaker(fail_threshold=3, timeout=5)
    
    def failing_func():
        raise Exception("Test failure")
    
    for i in range(5):
        try:
            breaker.call(failing_func)
        except Exception as e:
            print(f"Attempt {i+1}: {e}")
    
    print("Circuit breaker stats:", breaker.stats())
