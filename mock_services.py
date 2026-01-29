"""
Mock External Services for Testing
Simulates STT, LLM, and TTS services with different failure scenarios
"""

import random
import time
from exceptions import *


class MockSTTService:
    """Mock Speech-to-Text service"""

    def __init__(self, failure_rate=0.3):
        """
        Args:
            failure_rate: Probability of failure (0.0 to 1.0)
        """
        self.failure_rate = failure_rate
        self.call_count = 0

    def transcribe(self, audio_data):
        """
        Simulate speech-to-text transcription

        Args:
            audio_data: Simulated audio data

        Returns:
            Transcribed text

        Raises:
            Various exceptions to simulate failures
        """
        self.call_count += 1
        print(f"[STT] Service called (attempt #{self.call_count})")

        # Simulate processing time
        time.sleep(0.5)

        # Random failure scenarios
        if random.random() < self.failure_rate:
            scenario = random.choice([
                "timeout",
                "rate_limit",
                "network_error",
                "auth_error"
            ])

            if scenario == "timeout":
                raise TimeoutError("STT service timeout", service_name="STT")
            elif scenario == "rate_limit":
                raise RateLimitError("STT rate limit exceeded", service_name="STT")
            elif scenario == "network_error":
                raise NetworkError("STT network connection failed", service_name="STT")
            elif scenario == "auth_error":
                raise AuthenticationError("STT authentication failed", service_name="STT")

        # Success
        return "Hello, this is the transcribed text from audio"


class MockLLMService:
    """Mock Large Language Model service"""

    def __init__(self, failure_rate=0.3):
        """
        Args:
            failure_rate: Probability of failure (0.0 to 1.0)
        """
        self.failure_rate = failure_rate
        self.call_count = 0

    def generate_response(self, prompt):
        """
        Simulate LLM response generation

        Args:
            prompt: Input text prompt

        Returns:
            Generated response text

        Raises:
            Various exceptions to simulate failures
        """
        self.call_count += 1
        print(f"[LLM] Service called (attempt #{self.call_count})")

        # Simulate processing time
        time.sleep(0.5)

        # Random failure scenarios
        if random.random() < self.failure_rate:
            scenario = random.choice([
                "timeout",
                "service_unavailable",
                "quota_exceeded",
                "invalid_payload"
            ])

            if scenario == "timeout":
                raise TimeoutError("LLM service timeout", service_name="LLM")
            elif scenario == "service_unavailable":
                raise ServiceUnavailableError("LLM service unavailable", service_name="LLM")
            elif scenario == "quota_exceeded":
                raise QuotaExceededError("LLM quota exceeded", service_name="LLM")
            elif scenario == "invalid_payload":
                raise InvalidPayloadError("LLM invalid request", service_name="LLM")

        # Success
        return "This is a generated response from the AI assistant"


class MockTTSService:
    """Mock Text-to-Speech service"""

    def __init__(self, failure_rate=0.3):
        """
        Args:
            failure_rate: Probability of failure (0.0 to 1.0)
        """
        self.failure_rate = failure_rate
        self.call_count = 0

    def synthesize(self, text):
        """
        Simulate text-to-speech synthesis

        Args:
            text: Input text to convert to speech

        Returns:
            Simulated audio data

        Raises:
            Various exceptions to simulate failures
        """
        self.call_count += 1
        print(f"[TTS] Service called (attempt #{self.call_count})")

        # Simulate processing time
        time.sleep(0.5)

        # Random failure scenarios
        if random.random() < self.failure_rate:
            scenario = random.choice([
                "timeout",
                "network_error",
                "rate_limit",
                "resource_not_found"
            ])

            if scenario == "timeout":
                raise TimeoutError("TTS service timeout", service_name="TTS")
            elif scenario == "network_error":
                raise NetworkError("TTS network error", service_name="TTS")
            elif scenario == "rate_limit":
                raise RateLimitError("TTS rate limit exceeded", service_name="TTS")
            elif scenario == "resource_not_found":
                raise ResourceNotFoundError("TTS voice not found", service_name="TTS")

        # Success
        return b"<simulated_audio_data>"