"""
Alert System for Critical Errors
Sends notifications when critical issues occur
"""

import json
import os
from datetime import datetime


class AlertSystem:
    """
    Simple alert system that logs critical errors to a file
    In production, this would send emails/SMS/Slack messages
    """

    def __init__(self, alert_file="logs/alerts.json"):
        """
        Args:
            alert_file: Path to alerts file (default: logs/alerts.json)
        """
        self.alert_file = alert_file

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(alert_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Initialize alert file if it doesn't exist
        if not os.path.exists(alert_file):
            with open(alert_file, 'w') as f:
                json.dump([], f)

    def send_alert(self, severity, service_name, error_message, additional_info=None):
        """
        Send an alert for a critical error

        Args:
            severity: "LOW", "MEDIUM", "HIGH", "CRITICAL"
            service_name: Name of the failing service
            error_message: Description of the error
            additional_info: Any additional context (dict)
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "service_name": service_name,
            "error_message": error_message,
            "status": "UNRESOLVED"
        }

        if additional_info:
            alert["additional_info"] = additional_info

        # Read existing alerts
        try:
            with open(self.alert_file, 'r') as f:
                alerts = json.load(f)
        except:
            alerts = []

        # Add new alert
        alerts.append(alert)

        # Write back to file
        with open(self.alert_file, 'w') as f:
            json.dump(alerts, f, indent=2)

        # Print alert to console
        emoji = self._get_severity_emoji(severity)
        print(f"\n{emoji} ALERT [{severity}] - {service_name}")
        print(f"   Message: {error_message}")
        if additional_info:
            print(f"   Info: {additional_info}")
        print()

    def _get_severity_emoji(self, severity):
        """Get prefix for severity level"""
        prefixes = {
            "LOW": "[LOW]",
            "MEDIUM": "[MEDIUM]",
            "HIGH": "[HIGH]",
            "CRITICAL": "[CRITICAL]"
        }
        return prefixes.get(severity, "[ALERT]")

    def get_active_alerts(self):
        """Get all unresolved alerts"""
        try:
            with open(self.alert_file, 'r') as f:
                alerts = json.load(f)
            return [a for a in alerts if a.get("status") == "UNRESOLVED"]
        except:
            return []

    def resolve_alert(self, index):
        """Mark an alert as resolved"""
        try:
            with open(self.alert_file, 'r') as f:
                alerts = json.load(f)

            if 0 <= index < len(alerts):
                alerts[index]["status"] = "RESOLVED"
                alerts[index]["resolved_at"] = datetime.now().isoformat()

                with open(self.alert_file, 'w') as f:
                    json.dump(alerts, f, indent=2)

                print(f" [Alert] {index} marked as resolved")
        except Exception as e:
            print(f" [Error] resolving alert: {e}")

    def clear_alerts(self):
        """Clear all alerts"""
        with open(self.alert_file, 'w') as f:
            json.dump([], f)
        print("All alerts cleared")