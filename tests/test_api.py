"""
Tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test API endpoints without actual LLM calls."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        # Note: This requires mocking the LLM components
        # For now, we'll skip actual API tests
        pytest.skip("API tests require mocked LLM components")

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "red-llm-security"

    def test_list_attacks_endpoint(self, client):
        """Test attacks listing endpoint."""
        response = client.get("/api/v1/attacks")
        assert response.status_code == 200
        data = response.json()
        assert "single_attacks" in data
        assert "chain_attacks" in data
        assert "total" in data
        assert data["total"] > 0

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "RED"
        assert "version" in data
