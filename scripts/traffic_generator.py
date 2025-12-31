#!/usr/bin/env python3
"""
Traffic Generator for RED
========================
REQUIRED BY HACKATHON: Demonstrates detection rules in action.

This script generates interactions with the RED application that will
trigger all configured Datadog detection rules.
"""

import os
import sys
import time
import requests
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

console = Console()

BASE_URL = os.getenv("RED_API_URL", "http://localhost:8000")


def check_health():
    """Check if the RED application is running."""
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        return resp.status_code == 200
    except:
        return False


def run_attack(attack_id: str) -> dict:
    """Run a single attack."""
    resp = requests.post(f"{BASE_URL}/api/v1/attack/single", params={"attack_id": attack_id})
    return resp.json()


def run_assessment(categories: list = None, max_attacks: int = 10) -> dict:
    """Run an assessment."""
    resp = requests.post(
        f"{BASE_URL}/api/v1/attack/assessment",
        json={
            "categories": categories,
            "max_attacks": max_attacks,
            "include_chains": True
        }
    )
    return resp.json()


def trigger_detection_rules():
    """
    Run attacks designed to trigger each detection rule.
    This demonstrates all Datadog detection rules in action.
    """
    console.print("\n[bold red]🔴 RED Traffic Generator[/bold red]")
    console.print("Generating traffic to trigger Datadog detection rules...\n")

    # Check health
    if not check_health():
        console.print("[red]❌ RED application is not running![/red]")
        console.print(f"Start it with: uvicorn src.main:app --reload")
        return

    console.print("[green]✅ RED application is healthy[/green]\n")

    # Attack sets designed to trigger specific detection rules
    trigger_scenarios = [
        {
            "name": "Rule 1: Jailbreak Detection",
            "description": "Attacks that attempt to break model safety guardrails",
            "attacks": ["dan_classic", "kernel_mode", "dev_mode"],
        },
        {
            "name": "Rule 2: System Prompt Leak",
            "description": "Attacks targeting system instruction extraction",
            "attacks": ["system_prompt_direct", "completion_bait", "json_export"],
        },
        {
            "name": "Rule 3: PII Exfiltration",
            "description": "Attacks attempting to extract personal information",
            "attacks": ["pii_social_engineering", "training_data"],
        },
        {
            "name": "Rule 4: Credential Exposure",
            "description": "Attacks targeting API keys and passwords",
            "attacks": ["api_key_request", "db_credentials", "endpoint_discovery"],
        },
        {
            "name": "Rule 5: Prompt Injection",
            "description": "Direct prompt injection attempts",
            "attacks": ["ignore_previous", "delimiter_injection", "document_injection"],
        },
    ]

    results_table = Table(title="Detection Rule Trigger Results")
    results_table.add_column("Rule", style="cyan")
    results_table.add_column("Attack", style="white")
    results_table.add_column("Success", style="green")
    results_table.add_column("Severity", style="yellow")

    total_attacks = sum(len(s["attacks"]) for s in trigger_scenarios)
    completed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running attacks...", total=total_attacks)

        for scenario in trigger_scenarios:
            console.print(f"\n[bold]{scenario['name']}[/bold]")
            console.print(f"[dim]{scenario['description']}[/dim]")

            for attack_id in scenario["attacks"]:
                progress.update(task, description=f"Running {attack_id}...")

                try:
                    result = run_attack(attack_id)
                    success = "✅" if result.get("success") else "❌"
                    severity = result.get("severity", "unknown")

                    results_table.add_row(
                        scenario["name"][:30],
                        attack_id,
                        success,
                        severity
                    )

                except Exception as e:
                    results_table.add_row(
                        scenario["name"][:30],
                        attack_id,
                        "❌ Error",
                        str(e)[:20]
                    )

                completed += 1
                progress.update(task, completed=completed)
                time.sleep(1)  # Pace requests

    console.print("\n")
    console.print(results_table)

    # Summary
    console.print("\n[bold]Summary[/bold]")
    console.print("The above attacks have been sent to the RED application.")
    console.print("Check your Datadog dashboard for:")
    console.print("  • LLM Observability traces")
    console.print("  • Monitor alerts (detection rules)")
    console.print("  • Custom metrics (red.security.*)")
    console.print("  • Incidents (if critical vulnerabilities found)")
    console.print(f"\n[dim]Datadog URL: https://app.datadoghq.com/llm[/dim]")


def run_full_assessment():
    """Run a complete assessment for demo purposes."""
    console.print("\n[bold red]🔴 RED Full Assessment Demo[/bold red]\n")

    if not check_health():
        console.print("[red]❌ RED application is not running![/red]")
        return

    console.print("Running full security assessment...")
    console.print("This will execute 20 attacks across all categories.\n")

    start = datetime.now()
    report = run_assessment(max_attacks=20)
    duration = (datetime.now() - start).total_seconds()

    # Display results
    summary = report.get("summary", {})

    console.print(f"\n[bold]Assessment Complete[/bold]")
    console.print(f"Duration: {duration:.1f}s")
    console.print(f"Vulnerability Score: [bold red]{summary.get('vulnerability_score', 0)}[/bold red]/100")
    console.print(f"Risk Level: [bold]{summary.get('risk_level', 'UNKNOWN')}[/bold]")
    console.print(f"Success Rate: {summary.get('success_rate', 0)*100:.1f}%")

    # Show successful attacks
    successful = report.get("successful_attacks", [])
    if successful:
        console.print(f"\n[bold]Successful Attacks ({len(successful)}):[/bold]")
        for attack in successful[:5]:
            console.print(f"  • {attack.get('attack_name')}: {attack.get('severity')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RED Traffic Generator")
    parser.add_argument("--full", action="store_true", help="Run full assessment")
    parser.add_argument("--rules", action="store_true", help="Trigger all detection rules")
    args = parser.parse_args()

    if args.full:
        run_full_assessment()
    else:
        trigger_detection_rules()
