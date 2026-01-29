"""
Simple Logger for Error Tracking
Logs events to JSON file for easy analysis
"""

import json
import os
from datetime import datetime


class ErrorLogger:
    """
    Simple logger that writes structured logs to a JSON file
    """

    def __init__(self, log_file="logs/error_log.json"):
        """
        Args:
            log_file: Path to log file (default: logs/error_log.json)
        """
        self.log_file = log_file

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Initialize log file if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                json.dump([], f)

    def log_error(self, service_name, error_type, error_message,
                  retry_count=0, circuit_state="CLOSED", additional_info=None):
        """
        Log an error event

        Args:
            service_name: Name of the service that failed
            error_type: Type of error (e.g., "TransientError", "PermanentError")
            error_message: Error message
            retry_count: Number of retry attempts
            circuit_state: Current circuit breaker state
            additional_info: Any additional information (dict)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service_name": service_name,
            "error_type": error_type,
            "error_message": error_message,
            "retry_count": retry_count,
            "circuit_state": circuit_state
        }

        # Add additional info if provided
        if additional_info:
            log_entry["additional_info"] = additional_info

        # Read existing logs
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except:
            logs = []

        # Append new log
        logs.append(log_entry)

        # Write back to file
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        print(f"[LOGGED] {error_type} for {service_name}")

    def log_success(self, service_name, message="Operation successful"):
        """Log a successful operation"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service_name": service_name,
            "status": "SUCCESS",
            "message": message
        }

        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except:
            logs = []

        logs.append(log_entry)

        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        print(f"[LOGGED] Success for {service_name}")

    def log_circuit_state_change(self, service_name, old_state, new_state):
        """Log circuit breaker state changes"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "CIRCUIT_STATE_CHANGE",
            "service_name": service_name,
            "old_state": old_state,
            "new_state": new_state
        }

        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except:
            logs = []

        logs.append(log_entry)

        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        print(f"[LOGGED] Circuit state change for {service_name}: {old_state} -> {new_state}")

    def get_recent_logs(self, count=10):
        """Get most recent log entries"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            return logs[-count:]
        except:
            return []

    def clear_logs(self):
        """Clear all logs"""
        with open(self.log_file, 'w') as f:
            json.dump([], f)
        print("[INFO] Logs cleared")