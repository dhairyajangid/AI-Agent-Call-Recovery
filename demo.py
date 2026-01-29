"""
Demo Script - Test the Call Agent
Run this file to see the system in action!
"""

from call_agent import CallAgent
from mock_services import MockSTTService, MockLLMService, MockTTSService
import time


def run_demo():
    """
    Run a demo of the call agent with mock services
    """
    print("\n" + "="*60)
    print("  AI CALL AGENT - DEMO")
    print("="*60 + "\n")

    # Create mock services with 30% failure rate
    print("Initializing services...")
    stt_service = MockSTTService(failure_rate=0.3)
    llm_service = MockLLMService(failure_rate=0.3)
    tts_service = MockTTSService(failure_rate=0.3)
    print("Services initialized successfully\n")

    # Create the call agent
    print("Creating AI Call Agent...")
    agent = CallAgent(stt_service, llm_service, tts_service)
    print("Agent ready\n")

    # Simulate 5 calls
    print("Starting call simulations...\n")

    for i in range(1, 6):
        print(f"\n{'='*60}")
        print(f"CALL #{i}")
        print(f"{'='*60}")

        # Simulate audio input
        audio_input = f"<simulated_audio_call_{i}>"

        # Process the call
        result = agent.process_call(audio_input)

        if result:
            print(f"[SUCCESS] Call #{i} completed successfully")
        else:
            print(f"[FAILED] Call #{i} failed")

        # Small delay between calls
        if i < 5:
            print("\nWaiting 2 seconds before next call...")
            time.sleep(2)

    # Show final system status
    print("\n" + "="*60)
    print("FINAL SYSTEM STATUS")
    print("="*60)
    status = agent.get_system_status()

    print(f"\nSTT Circuit: {status['stt_circuit']['state']}")
    print(f"   Failures: {status['stt_circuit']['failure_count']}")

    print(f"\nLLM Circuit: {status['llm_circuit']['state']}")
    print(f"   Failures: {status['llm_circuit']['failure_count']}")

    print(f"\nTTS Circuit: {status['tts_circuit']['state']}")
    print(f"   Failures: {status['tts_circuit']['failure_count']}")

    print(f"\nRetry Configuration:")
    print(f"   Max Attempts: {status['retry_config']['max_attempts']}")
    print(f"   Initial Delay: {status['retry_config']['initial_delay']}s")

    print("\n" + "="*60)
    print("Check logs/ folder for detailed logs and alerts!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_demo()