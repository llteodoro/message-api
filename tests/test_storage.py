"""Tests for storage module."""

import pytest
from app.storage import MessageStorage


class TestMessageStorage:
    """Test message storage."""
    
    @pytest.fixture
    def storage(self):
        """Create a storage instance for each test."""
        return MessageStorage()
    
    def test_create_message(self, storage):
        """Test creating a message."""
        message = storage.create("Test message")
        assert message.text == "Test message"
        assert message.id.startswith("msg_")
        assert message.created_at is not None
    
    def test_get_all(self, storage):
        """Test getting all messages."""
        storage.create("Message 1")
        storage.create("Message 2")
        storage.create("Message 3")
        
        messages = storage.get_all()
        assert len(messages) == 3
    
    def test_get_by_id(self, storage):
        """Test getting a message by ID."""
        created = storage.create("Test message")
        retrieved = storage.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.text == created.text
    
    def test_get_by_id_not_found(self, storage):
        """Test getting a non-existent message."""
        result = storage.get_by_id("nonexistent")
        assert result is None
    
    def test_delete(self, storage):
        """Test deleting a message."""
        created = storage.create("Test message")
        result = storage.delete(created.id)
        
        assert result is True
        assert storage.get_by_id(created.id) is None
    
    def test_delete_not_found(self, storage):
        """Test deleting a non-existent message."""
        result = storage.delete("nonexistent")
        assert result is False
    
    def test_delete_all(self, storage):
        """Test deleting all messages."""
        storage.create("Message 1")
        storage.create("Message 2")
        storage.create("Message 3")
        
        count = storage.delete_all()
        assert count == 3
        assert len(storage.get_all()) == 0
    
    def test_get_all_texts(self, storage):
        """Test getting all message texts."""
        storage.create("Message 1")
        storage.create("Message 2")
        
        texts = storage.get_all_texts()
        assert "Message 1" in texts
        assert "Message 2" in texts
        assert len(texts) == 2
    
    def test_count(self, storage):
        """Test counting messages."""
        assert storage.count() == 0
        
        storage.create("Message 1")
        assert storage.count() == 1
        
        storage.create("Message 2")
        assert storage.count() == 2
        
        storage.delete_all()
        assert storage.count() == 0
