import os
import hashlib

# =====================================================
# TRY TO IMPORT REAL DILITHIUM (PQC SIGNATURE)
# =====================================================

try:
    from pqcrypto.sign.dilithium2 import (
        generate_keypair as dilithium_generate,
        sign as dilithium_sign,
        verify as dilithium_verify
    )
    _HAS_DILITHIUM = True
except Exception:
    _HAS_DILITHIUM = False

# =====================================================
# SIMULATION CONSTANTS
# =====================================================

SIMULATED_SIGN_SECRET = hashlib.sha256(
    b"simulated_dilithium_secret"
).digest()

# =====================================================
# DILITHIUM KEY GENERATION
# =====================================================

def generate_dilithium_keypair():
    """
    Returns (public_key, secret_key)
    """
    if _HAS_DILITHIUM:
        pk, sk = dilithium_generate()
        return bytes(pk), bytes(sk)
    else:
        # Simulated keys (sizes approx, not cryptographically real)
        return os.urandom(1312), os.urandom(2528)

# =====================================================
# DILITHIUM SIGN
# =====================================================

def dilithium_sign_message(secret_key: bytes, message: bytes) -> bytes:
    """
    Signs a message using Dilithium private key
    """
    if _HAS_DILITHIUM:
        signature = dilithium_sign(secret_key, message)
        return bytes(signature)
    else:
        # Simulation: hash(message || secret)
        return hashlib.sha256(message + SIMULATED_SIGN_SECRET).digest()

# =====================================================
# DILITHIUM VERIFY
# =====================================================

def dilithium_verify_signature(
    public_key: bytes,
    message: bytes,
    signature: bytes
) -> bool:
    """
    Verifies Dilithium signature
    """
    if _HAS_DILITHIUM:
        try:
            dilithium_verify(public_key, message, signature)
            return True
        except Exception:
            return False
    else:
        expected = hashlib.sha256(message + SIMULATED_SIGN_SECRET).digest()
        return signature == expected
