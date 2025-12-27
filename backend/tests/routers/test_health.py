"""
Health check endpoint tests.

Tests for the /api/v1/health endpoint.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_health_check_success(client: TestClient) -> None:
    """
    Test successful health check.

    Expected behavior: Returns 200 with healthy status.
    """
    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert "version" in data
    assert isinstance(data["version"], str)


def test_root_endpoint(client: TestClient) -> None:
    """
    Test root endpoint.

    Expected behavior: Returns API information.
    """
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert data["docs"] == "/api/docs"


def test_health_response_schema(client: TestClient) -> None:
    """
    Test health check response schema validation.

    Expected behavior: Response matches HealthResponse schema.
    """
    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Validate required fields
    required_fields = ["status", "version", "database"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Validate field types
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["database"], str)

    # Validate field values
    assert data["status"] in ["healthy", "unhealthy"]
    assert data["database"] in ["healthy", "unhealthy"]


@pytest.mark.parametrize(
    "endpoint,expected_status",
    [
        ("/api/v1/health", status.HTTP_200_OK),
        ("/", status.HTTP_200_OK),
        ("/api/docs", status.HTTP_200_OK),
    ],
)
def test_endpoint_accessibility(client: TestClient, endpoint: str, expected_status: int) -> None:
    """
    Test that important endpoints are accessible.

    Expected behavior: Endpoints return expected status codes.
    """
    response = client.get(endpoint)
    assert response.status_code == expected_status
