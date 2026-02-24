"""In-memory storage for messages."""

import uuid
from datetime import datetime, timezone
from threading import Lock
from typing import List, Optional, Dict
from app.models import Message


class MessageStorage:
    """Thread-safe in-memory storage for messages."""
    
    def __init__(self):
        """Initialize the storage."""
        self._messages: Dict[str, Message] = {}
        self._lock = Lock()
    
    def create(self, text: str) -> Message:
        """
        Create and store a new message.
        
        Args:
            text: The message text
            
        Returns:
            The created Message object
        """
        with self._lock:
            msg_id = f"msg_{uuid.uuid4().hex[:10]}"
            message = Message(
                id=msg_id,
                text=text,
                created_at=datetime.now(timezone.utc)
            )
            self._messages[msg_id] = message
            return message
    
    def get_all(self) -> List[Message]:
        """
        Get all messages.
        
        Returns:
            List of all stored messages
        """
        with self._lock:
            return list(self._messages.values())
    
    def get_by_id(self, message_id: str) -> Optional[Message]:
        """
        Get a message by ID.
        
        Args:
            message_id: The message ID
            
        Returns:
            The message or None if not found
        """
        with self._lock:
            return self._messages.get(message_id)
    
    def delete(self, message_id: str) -> bool:
        """
        Delete a message by ID.
        
        Args:
            message_id: The message ID
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if message_id in self._messages:
                del self._messages[message_id]
                return True
            return False
    
    def delete_all(self) -> int:
        """
        Delete all messages.
        
        Returns:
            Number of messages deleted
        """
        with self._lock:
            count = len(self._messages)
            self._messages.clear()
            return count
    
    def get_all_texts(self) -> set:
        """
        Get all message texts (for duplicate checking).
        
        Returns:
            Set of all message texts
        """
        with self._lock:
            return {msg.text for msg in self._messages.values()}
    
    def count(self) -> int:
        """
        Get the total count of messages.
        
        Returns:
            Number of stored messages
        """
        with self._lock:
            return len(self._messages)
