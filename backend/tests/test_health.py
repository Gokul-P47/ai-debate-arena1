"""Tests for the health check endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_up_status() -> None:
    """Health endpoint should return UP status and service name."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["service"] == "AI Debate Arena API"
