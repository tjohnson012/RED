"""
Datadog Incident Management integration.
"""

import os
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.incidents_api import IncidentsApi
from datadog_api_client.v2.model.incident_create_attributes import IncidentCreateAttributes
from datadog_api_client.v2.model.incident_create_data import IncidentCreateData
from datadog_api_client.v2.model.incident_create_request import IncidentCreateRequest
from datadog_api_client.v2.model.incident_type import IncidentType
from datadog_api_client.v2.model.incident_field_attributes_single_value import IncidentFieldAttributesSingleValue
from datadog_api_client.v2.model.incident_field_attributes_single_value_type import IncidentFieldAttributesSingleValueType


class IncidentManager:
    """Manages incident creation in Datadog."""

    def __init__(self):
        self.config = Configuration()
        self.config.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY")
        self.config.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY")
        self.config.server_variables["site"] = os.getenv("DD_SITE", "us5.datadoghq.com")

    def create_incident(self, attack_name: str, severity: str, leak_types: list,
                        evidence: str, response_snippet: str):
        """Create a Datadog incident for a successful attack."""

        severity_map = {
            "critical": "SEV-1",
            "high": "SEV-2",
            "medium": "SEV-3",
            "low": "SEV-4"
        }

        sev = severity_map.get(severity.lower(), "SEV-3")

        title = f"[RED] LLM Security Vulnerability: {attack_name}"

        summary = f"""
## Attack Details
- **Attack Name:** {attack_name}
- **Severity:** {severity.upper()}
- **Leaks Detected:** {', '.join(leak_types) if leak_types else 'None'}

## Evidence
{evidence}

## Response Snippet
```
{response_snippet[:500]}{'...' if len(response_snippet) > 500 else ''}
```

## Recommended Actions
1. Review system prompt for sensitive information exposure
2. Implement additional guardrails against this attack vector
3. Consider content filtering for responses
"""

        with ApiClient(self.config) as api_client:
            api = IncidentsApi(api_client)

            try:
                request = IncidentCreateRequest(
                    data=IncidentCreateData(
                        type=IncidentType.INCIDENTS,
                        attributes=IncidentCreateAttributes(
                            title=title,
                            fields={
                                "severity": IncidentFieldAttributesSingleValue(
                                    type=IncidentFieldAttributesSingleValueType("dropdown"),
                                    value=sev
                                ),
                            },
                        ),
                    )
                )

                response = api.create_incident(body=request)
                print(f"[DD] Incident created: {title}")
                return response.data.id

            except Exception as e:
                print(f"[DD] Failed to create incident: {e}")
                return None

    def create_security_incident(self, report: dict) -> dict:
        """
        Create a security incident from assessment report.

        REQUIRED BY HACKATHON:
        - Create actionable record inside Datadog
        - Include clear contextual information to drive next steps
        """
        summary = report.get("summary", {})

        # Determine severity based on findings
        if summary.get("vulnerability_score", 0) >= 70:
            severity = "SEV-1"
        elif summary.get("vulnerability_score", 0) >= 50:
            severity = "SEV-2"
        elif summary.get("vulnerability_score", 0) >= 30:
            severity = "SEV-3"
        else:
            severity = "SEV-4"

        # Build incident title
        title = f"[RED] Security Assessment: {summary.get('risk_level', 'UNKNOWN')} Risk - {summary.get('successful_attacks', 0)} Vulnerabilities Found"

        # Build detailed description with context
        successful_attacks = report.get("successful_attacks", [])

        attack_details = []
        for attack in successful_attacks[:5]:  # Top 5
            attack_details.append(
                f"- **{attack.get('attack_name', 'Unknown')}** ({attack.get('category', 'unknown')})\n"
                f"  - Severity: {attack.get('severity', 'unknown')}\n"
                f"  - Leak Types: {', '.join(attack.get('leak_types', []))}\n"
                f"  - Evidence: {attack.get('evidence', [])[:2]}"
            )

        description = f"""
## RED Team Security Assessment Report

### Summary
- **Session ID**: {report.get('session_id', 'N/A')}
- **Timestamp**: {report.get('timestamp', 'N/A')}
- **Duration**: {report.get('duration_seconds', 0):.1f} seconds
- **Vulnerability Score**: {summary.get('vulnerability_score', 0)}/100
- **Risk Level**: {summary.get('risk_level', 'UNKNOWN')}

### Attack Statistics
- **Total Attacks**: {summary.get('total_attacks', 0)}
- **Successful Attacks**: {summary.get('successful_attacks', 0)}
- **Success Rate**: {summary.get('success_rate', 0)*100:.1f}%

### Severity Breakdown
{self._format_severity_breakdown(report.get('by_severity', {}))}

### Top Successful Attacks
{chr(10).join(attack_details) if attack_details else 'No successful attacks'}

### Recommended Actions
1. Review and harden system prompts
2. Implement input validation and sanitization
3. Add output filtering for sensitive patterns
4. Consider rate limiting suspicious patterns
5. Enable Datadog LLM Observability security checks

### Runbook
[Link to LLM Security Hardening Runbook](https://docs.example.com/llm-security)

### Related Dashboards
- [RED Attack Dashboard](https://app.datadoghq.com/dashboard/red-attacks)
- [LLM Observability](https://app.datadoghq.com/llm)
"""

        try:
            with ApiClient(self.config) as api_client:
                api_instance = IncidentsApi(api_client)

                body = IncidentCreateRequest(
                    data=IncidentCreateData(
                        type=IncidentType("incidents"),
                        attributes=IncidentCreateAttributes(
                            title=title,
                            customer_impacted=summary.get("vulnerability_score", 0) >= 50,
                            fields={
                                "severity": IncidentFieldAttributesSingleValue(
                                    type=IncidentFieldAttributesSingleValueType("dropdown"),
                                    value=severity,
                                ),
                                "detection_method": IncidentFieldAttributesSingleValue(
                                    type=IncidentFieldAttributesSingleValueType("dropdown"),
                                    value="RED Team Assessment",
                                ),
                            },
                            notification_handles=[],
                        ),
                    ),
                )

                response = api_instance.create_incident(body=body)

                print(f"\n[DD] INCIDENT CREATED: {title}")
                print(f"     Severity: {severity}")
                print(f"     ID: {response.data.id}")

                return {
                    "incident_id": response.data.id,
                    "title": title,
                    "severity": severity,
                    "url": f"https://app.datadoghq.com/incidents/{response.data.id}"
                }

        except Exception as e:
            print(f"[DD] Failed to create incident: {e}")
            return {"error": str(e)}

    def _format_severity_breakdown(self, severities: dict) -> str:
        """Format severity breakdown for incident description."""
        lines = []
        for sev, count in severities.items():
            emoji = {"critical": "!", "high": "!", "medium": "*", "low": "-"}.get(sev, "-")
            lines.append(f"- {emoji} **{sev.upper()}**: {count}")
        return "\n".join(lines) if lines else "No vulnerabilities detected"


# Global instance
incidents = IncidentManager()
