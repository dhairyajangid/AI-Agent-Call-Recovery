"""
Main Call Agent - Orchestrates the entire call flow
This is the main class that handles STT -> LLM -> TTS pipeline
"""

from retry_manager import RetryManager
from circuit_breaker import CircuitBreaker
from logger import ErrorLogger
from alerts import AlertSystem
from exceptions import TransientError, PermanentError


class CallAgent:
    """
    Main AI Call Agent that coordinates all services
    Handles the complete flow: Audio -> Text -> AI Response -> Audio
    """

    def __init__(self, stt_service, llm_service, tts_service):
        """
        Initialize the call agent with all required services

        Args:
            stt_service: Speech-to-Text service instance
            llm_service: Large Language Model service instance
            tts_service: Text-to-Speech service instance
        """
        # Store service instances
        self.stt_service = stt_service
        self.llm_service = llm_service
        self.tts_service = tts_service

        # Initialize resilience components
        self.retry_manager = RetryManager(
            initial_delay=5,
            backoff_multiplier=2,
            max_attempts=3
        )

        # Create circuit breakers for each service
        self.stt_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=60,
            service_name="STT"
        )
        self.llm_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=60,
            service_name="LLM"
        )
        self.tts_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=60,
            service_name="TTS"
        )

        # Initialize logging and alerting
        self.logger = ErrorLogger()
        self.alert_system = AlertSystem()

    def process_call(self, audio_input):
        """
        Process a complete call flow

        Steps:
        1. Convert audio to text (STT)
        2. Generate AI response (LLM)
        3. Convert response to audio (TTS)

        Args:
            audio_input: Input audio data

        Returns:
            Final audio output or None if failed
        """
        print("\n" + "=" * 60)
        print("Starting Call Processing")
        print("=" * 60 + "\n")

        try:
            # Step 1: Speech-to-Text
            print("Step 1: Converting audio to text...")
            text = self._call_stt_service(audio_input)
            print(f"[SUCCESS] Transcribed: '{text}'\n")

            # Step 2: Generate AI Response
            print("Step 2: Generating AI response...")
            response = self._call_llm_service(text)
            print(f"[SUCCESS] AI Response: '{response}'\n")

            # Step 3: Text-to-Speech
            print("Step 3: Converting response to audio...")
            audio_output = self._call_tts_service(response)
            print(f"[SUCCESS] Audio generated successfully\n")

            print("=" * 60)
            print("Call Processing Completed Successfully!")
            print("=" * 60 + "\n")

            return audio_output



        except Exception as e:
            print("\n" + "=" * 60)
            print(f"[ERROR] Call Processing Failed: {str(e)}")
            print("=" * 60 + "\n")

    def _call_stt_service(self, audio_input):
        """
        Call Speech-to-Text service with retry and circuit breaker

        Args:
            audio_input: Audio data to transcribe

        Returns:
            Transcribed text

        Raises:
            Exception if service fails
        """
        try:
            # Wrap the service call with circuit breaker and retry
            result = self.retry_manager.execute_with_retry(
                func=lambda: self.stt_breaker.call(
                    self.stt_service.transcribe,
                    audio_input
                ),
                service_name="STT"
            )
            return result

        except TransientError as e:
            # Log transient error
            self.logger.log_error(
                service_name="STT",
                error_type="TransientError",
                error_message=e.message,
                circuit_state=self.stt_breaker.get_state()["state"]
            )
            # Send medium severity alert
            self.alert_system.send_alert(
                severity="MEDIUM",
                service_name="STT",
                error_message=f"Transient error: {e.message}"
            )
            raise

        except PermanentError as e:
            # Log permanent error
            self.logger.log_error(
                service_name="STT",
                error_type="PermanentError",
                error_message=e.message,
                circuit_state=self.stt_breaker.get_state()["state"]
            )
            # Send high severity alert for permanent errors
            self.alert_system.send_alert(
                severity="HIGH",
                service_name="STT",
                error_message=f"Permanent error: {e.message}"
            )
            raise

    def _call_llm_service(self, text):
        """
        Call LLM service with retry and circuit breaker

        Args:
            text: Input text prompt

        Returns:
            Generated response text

        Raises:
            Exception if service fails
        """
        try:
            # Wrap the service call with circuit breaker and retry
            result = self.retry_manager.execute_with_retry(
                func=lambda: self.llm_breaker.call(
                    self.llm_service.generate_response,
                    text
                ),
                service_name="LLM"
            )
            return result

        except TransientError as e:
            # Log transient error
            self.logger.log_error(
                service_name="LLM",
                error_type="TransientError",
                error_message=e.message,
                circuit_state=self.llm_breaker.get_state()["state"]
            )
            # Send medium severity alert
            self.alert_system.send_alert(
                severity="MEDIUM",
                service_name="LLM",
                error_message=f"Transient error: {e.message}"
            )
            raise

        except PermanentError as e:
            # Log permanent error
            self.logger.log_error(
                service_name="LLM",
                error_type="PermanentError",
                error_message=e.message,
                circuit_state=self.llm_breaker.get_state()["state"]
            )
            # Send high severity alert for permanent errors
            self.alert_system.send_alert(
                severity="HIGH",
                service_name="LLM",
                error_message=f"Permanent error: {e.message}"
            )
            raise

    def _call_tts_service(self, text):
        """
        Call Text-to-Speech service with retry and circuit breaker

        Args:
            text: Text to convert to speech

        Returns:
            Audio data

        Raises:
            Exception if service fails
        """
        try:
            # Wrap the service call with circuit breaker and retry
            result = self.retry_manager.execute_with_retry(
                func=lambda: self.tts_breaker.call(
                    self.tts_service.synthesize,
                    text
                ),
                service_name="TTS"
            )
            return result

        except TransientError as e:
            # Log transient error
            self.logger.log_error(
                service_name="TTS",
                error_type="TransientError",
                error_message=e.message,
                circuit_state=self.tts_breaker.get_state()["state"]
            )
            # Send medium severity alert
            self.alert_system.send_alert(
                severity="MEDIUM",
                service_name="TTS",
                error_message=f"Transient error: {e.message}"
            )
            raise

        except PermanentError as e:
            # Log permanent error
            self.logger.log_error(
                service_name="TTS",
                error_type="PermanentError",
                error_message=e.message,
                circuit_state=self.tts_breaker.get_state()["state"]
            )
            # Send high severity alert for permanent errors
            self.alert_system.send_alert(
                severity="HIGH",
                service_name="TTS",
                error_message=f"Permanent error: {e.message}"
            )
            raise

    def get_system_status(self):
        """
        Get current status of all systems

        Returns:
            Dictionary with status of all components
        """
        return {
            "stt_circuit": self.stt_breaker.get_state(),
            "llm_circuit": self.llm_breaker.get_state(),
            "tts_circuit": self.tts_breaker.get_state(),
            "retry_config": self.retry_manager.get_retry_info()
        }