#!/usr/bin/env python3
"""
Run RED Team Assessment
=======================
Standalone script to run a full red team assessment.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.observability.tracer import initialize_observability, shutdown_observability
from src.attacker.agent import RedTeamAgent


def main():
    """Run a full RED team assessment."""
    print("\n" + "=" * 60)
    print("🔴 RED - Adversarial LLM Security Testing")
    print("=" * 60)

    # Initialize observability
    initialize_observability()

    try:
        # Create agent and run assessment
        agent = RedTeamAgent()

        print("\nStarting security assessment...")
        print("This will test your LLM with various adversarial techniques.\n")

        # Run assessment
        report = agent.run_assessment(
            max_attacks=None,  # Run all attacks
            include_chains=True
        )

        # Print summary
        summary = report.get("summary", {})
        print("\n" + "=" * 60)
        print("📊 ASSESSMENT COMPLETE")
        print("=" * 60)
        print(f"\nSession ID: {report.get('session_id')}")
        print(f"Duration: {report.get('duration_seconds', 0):.1f} seconds")
        print(f"\nVulnerability Score: {summary.get('vulnerability_score', 0)}/100")
        print(f"Risk Level: {summary.get('risk_level', 'UNKNOWN')}")
        print(f"\nTotal Attacks: {summary.get('total_attacks', 0)}")
        print(f"Successful: {summary.get('successful_attacks', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0)*100:.1f}%")

        # Severity breakdown
        by_severity = report.get("by_severity", {})
        print("\nSeverity Breakdown:")
        print(f"  🔴 Critical: {by_severity.get('critical', 0)}")
        print(f"  🟠 High: {by_severity.get('high', 0)}")
        print(f"  🟡 Medium: {by_severity.get('medium', 0)}")
        print(f"  🟢 Low: {by_severity.get('low', 0)}")

        # Save report
        report_file = f"red_report_{report.get('session_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Full report saved to: {report_file}")

    finally:
        # Shutdown observability
        shutdown_observability()


if __name__ == "__main__":
    main()
