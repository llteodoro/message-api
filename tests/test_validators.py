"""Tests for validators module."""

import pytest
from app.validators import validate_message, is_duplicate


class TestValidateMessage:
    """Test message validation."""
    
    def test_valid_message(self):
        """Test validation of a valid message."""
        is_valid, error = validate_message("This is a valid message")
        assert is_valid is True
        assert error == ""
    
    def test_empty_message(self):
        """Test validation of an empty message."""
        is_valid, error = validate_message("")
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_whitespace_only(self):
        """Test validation of whitespace-only message."""
        is_valid, error = validate_message("   ")
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_too_short(self):
        """Test validation of message that's too short."""
        is_valid, error = validate_message("abc")
        assert is_valid is False
        assert "5 character" in error
    
    def test_too_long(self):
        """Test validation of message that's too long."""
        long_message = "a" * 201
        is_valid, error = validate_message(long_message)
        assert is_valid is False
        assert "200 character" in error
    
    def test_no_alphanumeric(self):
        """Test validation of message without alphanumeric characters."""
        is_valid, error = validate_message("!@#$%^&*()")
        assert is_valid is False
        assert "alphanumeric" in error
    
    def test_with_alphanumeric_and_special_chars(self):
        """Test validation of message with mixed characters."""
        is_valid, error = validate_message("Hello123!@#$%")
        assert is_valid is True
        assert error == ""
    
    def test_minimum_length(self):
        """Test message with minimum length."""
        is_valid, error = validate_message("12345")
        assert is_valid is True
        assert error == ""
    
    def test_maximum_length(self):
        """Test message with maximum length."""
        message = "a" * 200
        is_valid, error = validate_message(message)
        assert is_valid is True
        assert error == ""


class TestIsDuplicate:
    """Test duplicate detection."""
    
    def test_no_duplicates(self):
        """Test when message is not a duplicate."""
        existing = {"Hello world", "Test message"}
        result = is_duplicate("New message", existing)
        assert result is False
    
    def test_exact_duplicate(self):
        """Test exact duplicate detection."""
        existing = {"Hello world"}
        result = is_duplicate("Hello world", existing)
        assert result is True
    
    def test_case_insensitive_duplicate(self):
        """Test case-insensitive duplicate detection."""
        existing = {"Hello World"}
        result = is_duplicate("hello world", existing)
        assert result is True
    
    def test_duplicate_with_leading_trailing_spaces(self):
        """Test duplicate detection with leading/trailing spaces."""
        existing = {"  Hello World  "}
        result = is_duplicate("Hello World", existing)
        # Should be true because we strip before comparing
        assert result is True
    
    def test_empty_existing_set(self):
        """Test with empty existing messages set."""
        existing = set()
        result = is_duplicate("New message", existing)
        assert result is False
