"""
Retry Manager with Exponential Backoff
Handles retrying failed requests with increasing delays
"""

import time
from exceptions import TransientError, PermanentError


class RetryManager:
    """
    Manages retry logic with exponential backoff for transient errors
    """

    def __init__(self, initial_delay=5, backoff_multiplier=2, max_attempts=3):
        """
        Args:
            initial_delay: Starting delay in seconds (default: 5)
            backoff_multiplier: Multiply delay by this factor each retry (default: 2)
            max_attempts: Maximum retry attempts (default: 3)
        """
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_attempts = max_attempts

    def execute_with_retry(self, func, service_name, *args, **kwargs):
        """
        Execute a function with retry logic

        Args:
            func: Function to execute
            service_name: Name of the service being called
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Result from the function

        Raises:
            Exception if all retries fail
        """
        attempt = 0
        current_delay = self.initial_delay

        while attempt < self.max_attempts:
            try:
                # Try to execute the function
                result = func(*args, **kwargs)

                # If successful, return result
                if attempt > 0:
                    print(f"[SUCCESS] {service_name} succeeded after {attempt} retries")
                return result

            except TransientError as e:
                attempt += 1
                print(f"[WARNING] Attempt {attempt}/{self.max_attempts} failed for {service_name}: {e.message}")

                if attempt >= self.max_attempts:
                    # All retries exhausted
                    print(f"[ERROR] All retries exhausted for {service_name}")
                    raise e

                # Wait before retrying (exponential backoff)
                print(f"[INFO] Waiting {current_delay} seconds before retry...")
                time.sleep(current_delay)

                # Increase delay for next retry (exponential backoff)
                # Example: 5s -> 10s -> 20s
                current_delay *= self.backoff_multiplier


            except PermanentError as e:
                # Don't retry permanent errors
                print(f"[ERROR] Permanent error for {service_name}: {e.message}")
                print("[INFO] Not retrying (permanent error)")
                raise e

            except Exception as e:
                # Unknown error - treat as permanent
                print(f"[ERROR] Unknown error for {service_name}: {str(e)}")
                raise e

    def get_retry_info(self):
        """Get current retry configuration"""
        return {
            "initial_delay": self.initial_delay,
            "backoff_multiplier": self.backoff_multiplier,
            "max_attempts": self.max_attempts
        }