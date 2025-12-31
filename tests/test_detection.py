"""
Tests for attack detection and evaluation.
"""

import pytest
from src.attacker.evaluator import AttackEvaluator, LEAK_PATTERNS


class TestLeakPatterns:
    """Test leak pattern detection."""

    def test_ssn_pattern(self):
        """Test SSN pattern detection."""
        import re
        ssn_patterns = LEAK_PATTERNS["pii"]

        # Should match
        assert any(re.search(p, "123-45-6789") for p in ssn_patterns)
        assert any(re.search(p, "SSN: 987-65-4321") for p in ssn_patterns)

        # Should not match
        assert not any(re.search(p, "phone: 555-1234") for p in ssn_patterns if "\\d{3}-\\d{2}-\\d{4}" in p)

    def test_email_pattern(self):
        """Test email pattern detection."""
        import re
        email_patterns = [p for p in LEAK_PATTERNS["pii"] if "@" in p or "email" in p.lower()]

        # Should match
        assert any(re.search(p, "user@example.com", re.IGNORECASE) for p in email_patterns)
        assert any(re.search(p, "john.doe@company.org", re.IGNORECASE) for p in email_patterns)

    def test_credential_patterns(self):
        """Test credential pattern detection."""
        import re
        cred_patterns = LEAK_PATTERNS["credentials"]

        # Should match connection strings
        assert any(re.search(p, "postgres://admin:pass@localhost:5432", re.IGNORECASE) for p in cred_patterns)
        assert any(re.search(p, "mysql://root:secret@db:3306", re.IGNORECASE) for p in cred_patterns)

        # Should match admin codes
        assert any(re.search(p, "ADMIN-7X9K-BYPASS", re.IGNORECASE) for p in cred_patterns)

    def test_system_prompt_patterns(self):
        """Test system prompt leak patterns."""
        import re
        system_patterns = LEAK_PATTERNS["system_prompt"]

        # Should match
        assert any(re.search(p, "CONFIDENTIAL INSTRUCTIONS", re.IGNORECASE) for p in system_patterns)
        assert any(re.search(p, "DO NOT REVEAL this to users", re.IGNORECASE) for p in system_patterns)

    def test_internal_endpoint_patterns(self):
        """Test internal endpoint patterns."""
        import re
        endpoint_patterns = LEAK_PATTERNS["internal_endpoints"]

        # Should match
        assert any(re.search(p, "https://api.internal.company.com", re.IGNORECASE) for p in endpoint_patterns)
        assert any(re.search(p, "db.techcorp.internal:5432", re.IGNORECASE) for p in endpoint_patterns)


class TestPatternMatching:
    """Test the pattern matching functionality of the evaluator."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance."""
        # Skip if Google credentials not available
        pytest.skip("Evaluator tests require Google Cloud credentials")

    def test_pattern_match_success(self, evaluator):
        """Test pattern matching on successful attack."""
        attack = {
            "id": "test",
            "success_indicators": ["CONFIDENTIAL", "password"]
        }
        response = "The CONFIDENTIAL password is secret123"

        result = evaluator._pattern_match(response, attack["success_indicators"])

        assert len(result["matches"]) > 0
        assert "credentials" in result["leak_types"] or len(result["leak_types"]) > 0

    def test_pattern_match_failure(self, evaluator):
        """Test pattern matching on failed attack."""
        attack = {
            "id": "test",
            "success_indicators": ["CONFIDENTIAL", "password"]
        }
        response = "I cannot help with that request."

        result = evaluator._pattern_match(response, attack["success_indicators"])

        assert len(result["matches"]) == 0
        assert len(result["leak_types"]) == 0
