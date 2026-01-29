"""
Circuit Breaker Pattern Implementation
Prevents cascading failures by stopping calls to failing services
"""

import time
from enum import Enum


class CircuitState(Enum):
    """Three states of a circuit breaker"""
    CLOSED = "CLOSED"  # Normal operation - requests allowed
    OPEN = "OPEN"  # Service is failing - requests blocked
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures

    States:
    - CLOSED: Everything normal, requests go through
    - OPEN: Too many failures, block all requests
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(self, failure_threshold=3, timeout=60, service_name="Unknown"):
        """
        Args:
            failure_threshold: Number of failures before opening circuit (default: 3)
            timeout: Seconds to wait before trying half-open (default: 60)
            service_name: Name of the service this protects
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.service_name = service_name

        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0

    def call(self, func, *args, **kwargs):
        """
        Execute function through circuit breaker

        Args:
            func: Function to execute
            *args, **kwargs: Arguments for the function

        Returns:
            Result from function

        Raises:
            Exception if circuit is open or function fails
        """
        # Check if we should try to recover from OPEN state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                print(f"[INFO] Circuit breaker for {self.service_name} entering HALF_OPEN state (testing recovery)")
                self.state = CircuitState.HALF_OPEN
            else:
                # Circuit still open, fail fast
                raise Exception(f" [Circuit breaker] OPEN for {self.service_name} - failing fast")

        try:
            # Try to execute the function
            result = func(*args, **kwargs)

            # Success!
            self._on_success()
            return result

        except Exception as e:
            # Function failed
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful request"""
        if self.state == CircuitState.HALF_OPEN:
            # Success in half-open state - close the circuit
            print(f"[SUCCESS] Circuit breaker for {self.service_name} CLOSING (service recovered)")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Failed in half-open - go back to open
            print(f"[WARNING] Circuit breaker for {self.service_name} back to OPEN (still failing)")
            self.state = CircuitState.OPEN

        elif self.state == CircuitState.CLOSED:
            # Check if we should open the circuit
            if self.failure_count >= self.failure_threshold:
                print(f"[WARNING] Circuit breaker for {self.service_name} OPENING ({self.failure_count} failures)")
                self.state = CircuitState.OPEN

    def _should_attempt_reset(self):
        """Check if enough time has passed to try half-open state"""
        if self.last_failure_time is None:
            return False

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.timeout

    def get_state(self):
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "service_name": self.service_name
        }

    def reset(self):
        """Manually reset the circuit breaker"""
        print(f"[INFO] Manually resetting circuit breaker for {self.service_name}")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None