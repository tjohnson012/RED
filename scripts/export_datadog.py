#!/usr/bin/env python3
"""
Export Datadog Configurations to JSON
=====================================
REQUIRED BY HACKATHON: Export monitors, dashboards, SLOs to JSON.
"""

import os
import json
from datetime import datetime
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.api.service_level_objectives_api import ServiceLevelObjectivesApi


def get_configuration():
    """Get Datadog API configuration."""
    config = Configuration()
    config.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY")
    config.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY")
    site = os.getenv("DD_SITE", "datadoghq.com")
    config.server_variables["site"] = site
    return config


def export_monitors(output_dir: str):
    """Export all RED monitors."""
    config = get_configuration()

    with ApiClient(config) as api_client:
        api = MonitorsApi(api_client)
        monitors = api.list_monitors(tags="service:red-llm-security")

        monitors_data = []
        for monitor in monitors:
            monitors_data.append({
                "id": monitor.id,
                "name": monitor.name,
                "type": monitor.type,
                "query": monitor.query,
                "message": monitor.message,
                "tags": monitor.tags,
                "options": monitor.options.to_dict() if monitor.options else {},
            })

        output_path = os.path.join(output_dir, "monitors.json")
        with open(output_path, "w") as f:
            json.dump(monitors_data, f, indent=2, default=str)

        print(f"✅ Exported {len(monitors_data)} monitors to {output_path}")
        return monitors_data


def export_dashboard(dashboard_id: str, output_dir: str):
    """Export a specific dashboard."""
    config = get_configuration()

    with ApiClient(config) as api_client:
        api = DashboardsApi(api_client)
        dashboard = api.get_dashboard(dashboard_id)

        dashboard_data = {
            "id": dashboard.id,
            "title": dashboard.title,
            "description": dashboard.description,
            "layout_type": dashboard.layout_type,
            "widgets": [w.to_dict() for w in dashboard.widgets],
            "template_variables": [tv.to_dict() for tv in dashboard.template_variables] if dashboard.template_variables else [],
        }

        output_path = os.path.join(output_dir, "dashboard.json")
        with open(output_path, "w") as f:
            json.dump(dashboard_data, f, indent=2, default=str)

        print(f"✅ Exported dashboard '{dashboard.title}' to {output_path}")
        return dashboard_data


def export_slos(output_dir: str):
    """Export all RED SLOs."""
    config = get_configuration()

    with ApiClient(config) as api_client:
        api = ServiceLevelObjectivesApi(api_client)
        slos = api.list_slos(tags_query="service:red-llm-security")

        slos_data = []
        for slo in slos.data:
            slos_data.append({
                "id": slo.id,
                "name": slo.name,
                "type": slo.type,
                "description": slo.description,
                "tags": slo.tags,
                "thresholds": [t.to_dict() for t in slo.thresholds] if slo.thresholds else [],
            })

        output_path = os.path.join(output_dir, "slos.json")
        with open(output_path, "w") as f:
            json.dump(slos_data, f, indent=2, default=str)

        print(f"✅ Exported {len(slos_data)} SLOs to {output_path}")
        return slos_data


def create_sample_configs(output_dir: str):
    """Create sample configuration files if none exist in Datadog."""

    # Sample monitors
    monitors = [
        {
            "name": "[RED] Jailbreak Success Detected",
            "type": "metric alert",
            "query": "sum(last_5m):sum:red.security.attack.success{severity:high OR severity:critical} > 3",
            "message": """
🔴 **RED Alert: Successful Jailbreak Attacks Detected**

Multiple high/critical severity jailbreak attacks have succeeded against your LLM application.

**What this means:**
- Attackers can bypass your AI's safety guardrails
- Your system prompt may be exposed
- Confidential data could be at risk

**Immediate Actions:**
1. Review LLM Observability traces
2. Check for leaked information
3. Consider implementing stricter input validation

@slack-security-alerts
""",
            "tags": ["service:red-llm-security", "category:jailbreak", "team:security"],
            "options": {
                "thresholds": {"critical": 3, "warning": 1},
                "notify_no_data": False,
                "renotify_interval": 60
            }
        },
        {
            "name": "[RED] System Prompt Leaked",
            "type": "log alert",
            "query": 'logs("service:red-llm-security leak_type:system_prompt").index("*").rollup("count").by("attack_id").last("15m") > 0',
            "message": """
🔴 **RED Alert: System Prompt Leakage Detected**

Your LLM's system prompt has been extracted through an attack.

**Severity: HIGH**

**Exposed Information:**
- System instructions
- Behavioral guidelines
- Potentially confidential business logic

**Immediate Actions:**
1. Rotate sensitive configuration if exposed
2. Review the attack trace in LLM Observability
3. Implement system prompt protection

@pagerduty-security
""",
            "tags": ["service:red-llm-security", "category:leak", "leak_type:system_prompt"],
        },
        {
            "name": "[RED] PII Exfiltration Alert",
            "type": "metric alert",
            "query": "sum(last_10m):sum:red.security.leak.detected{leak_type:pii} > 0",
            "message": """
🔴 **CRITICAL: PII Data Exfiltration Detected**

Personal Identifiable Information (PII) has been leaked through your LLM application.

**This is a potential data breach.**

**Immediate Actions:**
1. Identify affected data subjects
2. Review compliance implications (GDPR, CCPA)
3. Initiate incident response procedures

@incident-response @legal-team
""",
            "tags": ["service:red-llm-security", "category:pii", "compliance:critical"],
            "options": {"thresholds": {"critical": 0}}
        },
        {
            "name": "[RED] Credential Exposure Detected",
            "type": "metric alert",
            "query": "sum(last_5m):sum:red.security.leak.detected{leak_type:credentials} > 0",
            "message": """
🔴 **CRITICAL: Credentials Exposed**

API keys, passwords, or other credentials have been leaked.

**Immediate Actions:**
1. ROTATE ALL EXPOSED CREDENTIALS IMMEDIATELY
2. Review access logs for unauthorized use
3. Check for lateral movement

@security-ops @incident-commander
""",
            "tags": ["service:red-llm-security", "category:credentials", "severity:critical"],
            "options": {"thresholds": {"critical": 0}}
        },
        {
            "name": "[RED] Attack Success Rate Anomaly",
            "type": "metric alert",
            "query": "avg(last_15m):avg:red.security.assessment.success_rate{*} > 30",
            "message": """
⚠️ **Warning: High Attack Success Rate**

Your LLM application is showing a high vulnerability to attacks.

**Success Rate:** {{value}}%

This indicates systemic security weaknesses that need attention.

**Recommended Actions:**
1. Review recent security assessment report
2. Prioritize fixing high/critical vulnerabilities
3. Consider additional security hardening

@security-team
""",
            "tags": ["service:red-llm-security", "category:anomaly"],
            "options": {"thresholds": {"critical": 50, "warning": 30}}
        }
    ]

    with open(os.path.join(output_dir, "monitors.json"), "w") as f:
        json.dump(monitors, f, indent=2)
    print(f"✅ Created sample monitors.json")

    # Sample dashboard
    dashboard = {
        "title": "RED Attack Dashboard",
        "description": "Security assessment dashboard for RED LLM testing",
        "layout_type": "ordered",
        "widgets": [
            {
                "definition": {
                    "title": "Vulnerability Score",
                    "type": "query_value",
                    "requests": [{"q": "avg:red.security.assessment.vulnerability_score{*}"}],
                    "precision": 0,
                    "custom_unit": "/100"
                }
            },
            {
                "definition": {
                    "title": "Attack Success Rate",
                    "type": "query_value",
                    "requests": [{"q": "avg:red.security.assessment.success_rate{*}"}],
                    "precision": 1,
                    "custom_unit": "%"
                }
            },
            {
                "definition": {
                    "title": "Total Attacks",
                    "type": "query_value",
                    "requests": [{"q": "sum:red.security.attack.count{*}.as_count()"}]
                }
            },
            {
                "definition": {
                    "title": "Successful Attacks",
                    "type": "query_value",
                    "requests": [{"q": "sum:red.security.attack.success{*}.as_count()"}]
                }
            },
            {
                "definition": {
                    "title": "Attacks by Category",
                    "type": "toplist",
                    "requests": [{"q": "sum:red.security.attack.count{*} by {category}.as_count()"}]
                }
            },
            {
                "definition": {
                    "title": "Attacks by Severity",
                    "type": "sunburst",
                    "requests": [{"q": "sum:red.security.attack.success{*} by {severity}.as_count()"}]
                }
            },
            {
                "definition": {
                    "title": "Attack Timeline",
                    "type": "timeseries",
                    "requests": [
                        {"q": "sum:red.security.attack.success{*}.as_count()", "display_type": "bars"},
                        {"q": "sum:red.security.attack.failure{*}.as_count()", "display_type": "bars"}
                    ]
                }
            },
            {
                "definition": {
                    "title": "Leak Types Detected",
                    "type": "toplist",
                    "requests": [{"q": "sum:red.security.leak.detected{*} by {leak_type}.as_count()"}]
                }
            },
            {
                "definition": {
                    "title": "Detection Rules Status",
                    "type": "manage_status",
                    "query": "service:red-llm-security",
                    "display_format": "counts_and_list"
                }
            },
            {
                "definition": {
                    "title": "Attack Latency",
                    "type": "timeseries",
                    "requests": [{"q": "avg:red.security.attack.latency{*}"}]
                }
            }
        ]
    }

    with open(os.path.join(output_dir, "dashboard.json"), "w") as f:
        json.dump(dashboard, f, indent=2)
    print(f"✅ Created sample dashboard.json")

    # Sample SLOs
    slos = [
        {
            "name": "LLM Security - Low Attack Success Rate",
            "type": "metric",
            "description": "Maintain low attack success rate against LLM application",
            "tags": ["service:red-llm-security", "team:security"],
            "thresholds": [
                {"timeframe": "7d", "target": 80.0, "warning": 90.0},
                {"timeframe": "30d", "target": 85.0, "warning": 90.0}
            ],
            "query": {
                "numerator": "sum:red.security.attack.failure{*}.as_count()",
                "denominator": "sum:red.security.attack.count{*}.as_count()"
            }
        },
        {
            "name": "LLM Security - No Critical Leaks",
            "type": "metric",
            "description": "Zero critical data leaks (credentials, PII)",
            "tags": ["service:red-llm-security", "compliance:critical"],
            "thresholds": [
                {"timeframe": "7d", "target": 100.0},
                {"timeframe": "30d", "target": 100.0}
            ],
            "query": {
                "numerator": "sum:red.security.attack.count{severity:NOT IN (critical)}.as_count()",
                "denominator": "sum:red.security.attack.count{*}.as_count()"
            }
        }
    ]

    with open(os.path.join(output_dir, "slos.json"), "w") as f:
        json.dump(slos, f, indent=2)
    print(f"✅ Created sample slos.json")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export Datadog configurations")
    parser.add_argument("--output", "-o", default="datadog", help="Output directory")
    parser.add_argument("--dashboard-id", help="Specific dashboard ID to export")
    parser.add_argument("--sample", action="store_true", help="Create sample configs")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if args.sample:
        create_sample_configs(args.output)
    else:
        try:
            export_monitors(args.output)
            if args.dashboard_id:
                export_dashboard(args.dashboard_id, args.output)
            export_slos(args.output)
        except Exception as e:
            print(f"⚠️ Could not export from Datadog: {e}")
            print("Creating sample configurations instead...")
            create_sample_configs(args.output)
