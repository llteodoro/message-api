"""Tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from app.main import app, storage, metrics


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_storage_and_metrics():
    """Reset storage and metrics before each test."""
    storage.delete_all()
    # Reset metrics
    metrics.total_requests = 0
    metrics.successful_requests = 0
    metrics.failed_requests = 0
    metrics.requests_by_type.clear()
    metrics.response_codes.clear()
    metrics.creation_attempts = 0
    metrics.successful_creations = 0
    metrics.failed_creations = 0
    yield
    storage.delete_all()
    # Reset metrics
    metrics.total_requests = 0
    metrics.successful_requests = 0
    metrics.failed_requests = 0
    metrics.requests_by_type.clear()
    metrics.response_codes.clear()
    metrics.creation_attempts = 0
    metrics.successful_creations = 0
    metrics.failed_creations = 0


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] is not None


class TestMessageCreation:
    """Test message creation endpoint."""
    
    def test_create_valid_message(self, client):
        """Test creating a valid message."""
        response = client.post(
            "/messages",
            json={"text": "This is a valid message"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "This is a valid message"
        assert data["id"].startswith("msg_")
    
    def test_create_message_too_short(self, client):
        """Test creating a message that's too short."""
        response = client.post(
            "/messages",
            json={"text": "abc"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "5 character" in data["message"]
    
    def test_create_message_too_long(self, client):
        """Test creating a message that's too long."""
        long_text = "a" * 201
        response = client.post(
            "/messages",
            json={"text": long_text}
        )
        # Pydantic validates max_length constraint, returns 422
        assert response.status_code in [400, 422]
    
    def test_create_message_no_alphanumeric(self, client):
        """Test creating a message without alphanumeric characters."""
        response = client.post(
            "/messages",
            json={"text": "!@#$%^&*()"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "alphanumeric" in data["message"]
    
    def test_create_duplicate_message(self, client):
        """Test creating a duplicate message."""
        # Create first message
        client.post("/messages", json={"text": "This is a message"})
        
        # Try to create duplicate
        response = client.post(
            "/messages",
            json={"text": "This is a message"}
        )
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == "DUPLICATE_MESSAGE"
    
    def test_create_duplicate_case_insensitive(self, client):
        """Test duplicate detection is case-insensitive."""
        # Create first message
        client.post("/messages", json={"text": "This is a message"})
        
        # Try to create duplicate with different case
        response = client.post(
            "/messages",
            json={"text": "this is a message"}
        )
        assert response.status_code == 409


class TestMessageRetrieval:
    """Test message retrieval endpoints."""
    
    def test_get_all_empty(self, client):
        """Test getting all messages when none exist."""
        response = client.get("/messages")
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_get_all_messages(self, client):
        """Test getting all messages."""
        client.post("/messages", json={"text": "Message 1"})
        client.post("/messages", json={"text": "Message 2"})
        
        response = client.get("/messages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_message_by_id(self, client):
        """Test getting a message by ID."""
        create_response = client.post(
            "/messages",
            json={"text": "Test message"}
        )
        message_id = create_response.json()["id"]
        
        response = client.get(f"/messages/{message_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == message_id
        assert data["text"] == "Test message"
    
    def test_get_message_not_found(self, client):
        """Test getting a non-existent message."""
        response = client.get("/messages/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "MESSAGE_NOT_FOUND"


class TestMessageDeletion:
    """Test message deletion endpoints."""
    
    def test_delete_message(self, client):
        """Test deleting a message."""
        create_response = client.post(
            "/messages",
            json={"text": "Message to delete"}
        )
        message_id = create_response.json()["id"]
        
        response = client.delete(f"/messages/{message_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/messages/{message_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_message(self, client):
        """Test deleting a non-existent message."""
        response = client.delete("/messages/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "MESSAGE_NOT_FOUND"
    
    def test_delete_all_messages(self, client):
        """Test deleting all messages."""
        client.post("/messages", json={"text": "Message 1"})
        client.post("/messages", json={"text": "Message 2"})
        
        response = client.delete("/messages")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 2
        
        # Verify all deleted
        get_response = client.get("/messages")
        assert get_response.json() == []


class TestMetrics:
    """Test metrics endpoint."""
    
    def test_get_metrics_empty_state(self, client):
        """Test getting metrics in empty state."""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_messages"] == 0
        # Verify structure of metrics
        assert "total_requests" in data
        assert "successful_requests" in data
        assert "failed_requests" in data
        assert "requests_by_type" in data
        assert "response_codes" in data
    
    def test_metrics_track_creation(self, client):
        """Test that metrics track message creation."""
        # Create some messages
        for i in range(3):
            client.post("/messages", json={"text": f"Message {i+1}"})
        
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_messages"] == 3
        assert data["successful_creations"] == 3
    
    def test_metrics_track_failures(self, client):
        """Test that metrics track failed operations."""
        # Create a valid message
        client.post("/messages", json={"text": "Valid message"})
        
        # Try to create invalid messages
        client.post("/messages", json={"text": "abc"})  # Too short
        client.post("/messages", json={"text": "!@#$%"})  # No alphanumeric
        
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["successful_creations"] == 1
        assert data["failed_creations"] == 2


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "documentation" in data
