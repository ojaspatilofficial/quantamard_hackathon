"""
Message Integrity Layer using HMAC-SHA256
==========================================
This module provides message integrity verification without modifying existing code.
It extends message payloads with an 'integrity' field containing HMAC signatures.

Usage:
    - Before sending: add_message_integrity(message_data)
    - After receiving: verify_message_integrity(message_data)
"""

import hmac
import hashlib
import os
import json
from typing import Dict, Any, Tuple


# ============================================================================
# SECRET KEY MANAGEMENT
# ============================================================================

def get_hmac_secret() -> bytes:
    """
    Retrieve HMAC secret key from environment or generate a persistent one.
    
    Priority:
    1. Environment variable CRYPTEXQ_HMAC_SECRET
    2. Auto-generated key stored in .hmac_secret file (for development)
    
    Returns:
        bytes: 32-byte secret key for HMAC operations
    """
    # Try environment variable first (production use)
    env_secret = os.environ.get('CRYPTEXQ_HMAC_SECRET')
    if env_secret:
        return env_secret.encode('utf-8')
    
    # For development: use/create a persistent file-based secret
    secret_file = os.path.join(os.path.dirname(__file__), '.hmac_secret')
    
    if os.path.exists(secret_file):
        with open(secret_file, 'rb') as f:
            return f.read()
    else:
        # Generate new secret and store it
        new_secret = os.urandom(32)
        with open(secret_file, 'wb') as f:
            f.write(new_secret)
        print(f"[HMAC INTEGRITY] Generated new secret key: {secret_file}")
        return new_secret


# ============================================================================
# HMAC GENERATION
# ============================================================================

def generate_hmac(message_content: str, timestamp: str, sender_id: str, secret: bytes) -> str:
    """
    Generate HMAC-SHA256 signature for message integrity.
    
    The HMAC is computed over: message + timestamp + senderId
    This ensures that any tampering with content, timing, or sender is detected.
    
    Args:
        message_content: The actual message content (can be ciphertext_b64)
        timestamp: Message timestamp (ISO format or Unix timestamp)
        sender_id: Identifier of the message sender
        secret: Secret key for HMAC computation
    
    Returns:
        str: Hexadecimal HMAC digest
    """
    # Concatenate all fields to protect
    data_to_sign = f"{message_content}|{timestamp}|{sender_id}"
    
    # Compute HMAC-SHA256
    h = hmac.new(secret, data_to_sign.encode('utf-8'), hashlib.sha256)
    
    return h.hexdigest()


def add_message_integrity(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add integrity field to outgoing message WITHOUT modifying original data.
    
    This function extends the message payload with an 'integrity' field containing
    the HMAC signature. The original message structure remains unchanged.
    
    Args:
        message_data: Original message dict with keys like 'from', 'to', 'ciphertext_b64', etc.
    
    Returns:
        Dict: Message data with added 'integrity' field
    
    Example:
        >>> msg = {"from": "Alice", "to": "Bob", "ciphertext_b64": "xyz..."}
        >>> secured_msg = add_message_integrity(msg)
        >>> # secured_msg now has: {..., "integrity": {"type": "HMAC_SHA256", "value": "abc..."}}
    """
    import time
    
    # Extract or generate timestamp
    if 'timestamp' not in message_data:
        message_data['timestamp'] = str(int(time.time() * 1000))  # milliseconds
    
    # Get message content (prioritize encrypted content)
    message_content = message_data.get('ciphertext_b64', '') or message_data.get('message', '')
    timestamp = message_data['timestamp']
    sender_id = message_data.get('from', 'unknown')
    
    # Get secret key
    secret = get_hmac_secret()
    
    # Generate HMAC
    hmac_value = generate_hmac(message_content, timestamp, sender_id, secret)
    
    # Add integrity field (extends payload without modifying existing fields)
    message_data['integrity'] = {
        'type': 'HMAC_SHA256',
        'value': hmac_value
    }
    
    return message_data


# ============================================================================
# HMAC VERIFICATION
# ============================================================================

def verify_message_integrity(message_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Verify message integrity by recomputing and comparing HMAC.
    
    This function checks if the message has been tampered with during transit.
    It recomputes the HMAC and compares it with the received value.
    
    Args:
        message_data: Received message dict with 'integrity' field
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - (True, "") if integrity check passes
            - (False, "reason") if integrity check fails
    
    Example:
        >>> is_valid, error = verify_message_integrity(received_msg)
        >>> if not is_valid:
        >>>     print(f"Message tampered: {error}")
    """
    # Check if integrity field exists
    if 'integrity' not in message_data:
        return False, "Missing integrity field - message may be from legacy sender"
    
    integrity_data = message_data['integrity']
    
    # Validate integrity field structure
    if not isinstance(integrity_data, dict):
        return False, "Invalid integrity field format"
    
    if integrity_data.get('type') != 'HMAC_SHA256':
        return False, f"Unsupported integrity type: {integrity_data.get('type')}"
    
    received_hmac = integrity_data.get('value')
    if not received_hmac:
        return False, "Missing HMAC value in integrity field"
    
    # Extract message components
    message_content = message_data.get('ciphertext_b64', '') or message_data.get('message', '')
    timestamp = message_data.get('timestamp', '')
    sender_id = message_data.get('from', 'unknown')
    
    if not timestamp:
        return False, "Missing timestamp - cannot verify integrity"
    
    # Get secret key
    secret = get_hmac_secret()
    
    # Recompute HMAC
    computed_hmac = generate_hmac(message_content, timestamp, sender_id, secret)
    
    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(received_hmac, computed_hmac):
        return False, "HMAC mismatch - message has been tampered with"
    
    # Integrity verified successfully
    return True, ""


# ============================================================================
# LOGGING & ERROR HANDLING
# ============================================================================

def log_integrity_failure(message_data: Dict[str, Any], reason: str):
    """
    Log integrity verification failures for security monitoring.
    
    Args:
        message_data: The message that failed verification
        reason: Description of why verification failed
    """
    sender = message_data.get('from', 'unknown')
    recipient = message_data.get('to', 'unknown')
    timestamp = message_data.get('timestamp', 'unknown')
    
    print(f"[INTEGRITY VIOLATION] {sender} → {recipient}")
    print(f"  Reason: {reason}")
    print(f"  Timestamp: {timestamp}")
    print(f"  Message preview: {str(message_data)[:100]}...")
    print("=" * 60)


def safe_reject_message(message_data: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """
    Safely reject a message that failed integrity check.
    
    Returns an error response without crashing the application.
    
    Args:
        message_data: The compromised message
        reason: Why the message was rejected
    
    Returns:
        Dict: Error response to send back to client
    """
    log_integrity_failure(message_data, reason)
    
    return {
        'error': 'MESSAGE_INTEGRITY_FAILED',
        'reason': 'Message integrity verification failed',
        'details': reason,
        'action': 'Message rejected for security reasons'
    }


# ============================================================================
# HELPER FUNCTIONS FOR INTEGRATION
# ============================================================================

def wrap_outgoing_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pre-send hook: Add integrity to outgoing messages.
    
    This is the main integration point for outgoing messages.
    Simply call this function before emitting a message.
    
    Args:
        message_data: Original message to send
    
    Returns:
        Dict: Message with integrity field added
    """
    try:
        return add_message_integrity(message_data)
    except Exception as e:
        print(f"[HMAC INTEGRITY] Warning: Failed to add integrity: {e}")
        # Return original message if integrity addition fails (non-breaking)
        return message_data


def unwrap_incoming_message(message_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Post-receive hook: Verify integrity of incoming messages.
    
    This is the main integration point for incoming messages.
    Call this function immediately after receiving a message.
    
    Args:
        message_data: Received message to verify
    
    Returns:
        Tuple[bool, Dict]: (is_valid, message_or_error)
            - If valid: (True, original_message)
            - If invalid: (False, error_response)
    
    Example:
        >>> is_valid, result = unwrap_incoming_message(received_data)
        >>> if not is_valid:
        >>>     emit("error", result)  # Send error back
        >>>     return
        >>> # Process valid message
        >>> process_message(result)
    """
    try:
        is_valid, error_reason = verify_message_integrity(message_data)
        
        if not is_valid:
            error_response = safe_reject_message(message_data, error_reason)
            return False, error_response
        
        # Valid message - return it unchanged
        return True, message_data
        
    except Exception as e:
        print(f"[HMAC INTEGRITY] Warning: Integrity check failed with exception: {e}")
        # In case of unexpected errors, log but don't crash
        error_response = safe_reject_message(message_data, f"Integrity check exception: {str(e)}")
        return False, error_response


if __name__ == "__main__":
    # Self-test
    print("HMAC Integrity Module - Self Test")
    print("=" * 60)
    
    # Test message
    test_msg = {
        "from": "Alice",
        "to": "Bob",
        "ciphertext_b64": "SGVsbG8gV29ybGQ=",
        "iv_b64": "random_iv_123"
    }
    
    print("\n1. Adding integrity to message...")
    secured_msg = add_message_integrity(test_msg.copy())
    print(f"   Integrity field: {secured_msg.get('integrity')}")
    
    print("\n2. Verifying valid message...")
    is_valid, error = verify_message_integrity(secured_msg)
    print(f"   Valid: {is_valid}, Error: {error or 'None'}")
    
    print("\n3. Testing tampered message...")
    tampered_msg = secured_msg.copy()
    tampered_msg['ciphertext_b64'] = "TAMPERED_DATA"
    is_valid, error = verify_message_integrity(tampered_msg)
    print(f"   Valid: {is_valid}, Error: {error}")
    
    print("\n4. Testing message without integrity field...")
    is_valid, error = verify_message_integrity(test_msg)
    print(f"   Valid: {is_valid}, Error: {error}")
    
    print("\n" + "=" * 60)
    print("Self-test completed!")
