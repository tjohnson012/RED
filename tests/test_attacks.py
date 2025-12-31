"""
Tests for attack library.
"""

import pytest
from src.attacker.attacks import (
    ALL_ATTACKS,
    ALL_CHAIN_ATTACKS,
    get_attacks_by_category,
    get_attacks_by_severity,
    get_attack_by_id
)


class TestAttackLibrary:
    """Test the attack library structure."""

    def test_all_attacks_loaded(self):
        """Verify all attacks are loaded."""
        assert len(ALL_ATTACKS) > 0
        assert len(ALL_ATTACKS) >= 30  # We have 30+ attacks

    def test_chain_attacks_loaded(self):
        """Verify chain attacks are loaded."""
        assert len(ALL_CHAIN_ATTACKS) > 0
        assert len(ALL_CHAIN_ATTACKS) >= 3

    def test_attack_structure(self):
        """Verify each attack has required fields."""
        required_fields = ["id", "name", "category", "prompt", "success_indicators", "severity"]
        for attack in ALL_ATTACKS:
            for field in required_fields:
                assert field in attack, f"Attack {attack.get('id', 'unknown')} missing field: {field}"

    def test_chain_attack_structure(self):
        """Verify chain attacks have required fields."""
        for chain in ALL_CHAIN_ATTACKS:
            assert "id" in chain
            assert "name" in chain
            assert "steps" in chain
            assert len(chain["steps"]) > 0
            for step in chain["steps"]:
                assert "prompt" in step
                assert "purpose" in step

    def test_get_attacks_by_category(self):
        """Test category filtering."""
        jailbreaks = get_attacks_by_category("jailbreak")
        assert len(jailbreaks) > 0
        for attack in jailbreaks:
            assert attack["category"] == "jailbreak"

        injections = get_attacks_by_category("injection")
        assert len(injections) > 0
        for attack in injections:
            assert attack["category"] == "injection"

    def test_get_attacks_by_severity(self):
        """Test severity filtering."""
        high_severity = get_attacks_by_severity("high")
        assert len(high_severity) > 0
        for attack in high_severity:
            assert attack["severity"] == "high"

        critical_severity = get_attacks_by_severity("critical")
        assert len(critical_severity) > 0
        for attack in critical_severity:
            assert attack["severity"] == "critical"

    def test_get_attack_by_id(self):
        """Test getting attack by ID."""
        attack = get_attack_by_id("dan_classic")
        assert attack is not None
        assert attack["id"] == "dan_classic"
        assert attack["name"] == "DAN Classic"

        # Test non-existent attack
        missing = get_attack_by_id("nonexistent_attack")
        assert missing is None

    def test_unique_attack_ids(self):
        """Verify all attack IDs are unique."""
        ids = [a["id"] for a in ALL_ATTACKS]
        assert len(ids) == len(set(ids)), "Duplicate attack IDs found"

    def test_valid_severity_levels(self):
        """Verify all severity levels are valid."""
        valid_severities = ["low", "medium", "high", "critical"]
        for attack in ALL_ATTACKS:
            assert attack["severity"] in valid_severities, f"Invalid severity: {attack['severity']}"

    def test_valid_categories(self):
        """Verify all categories are valid."""
        valid_categories = ["jailbreak", "injection", "extraction", "encoding"]
        for attack in ALL_ATTACKS:
            assert attack["category"] in valid_categories, f"Invalid category: {attack['category']}"
