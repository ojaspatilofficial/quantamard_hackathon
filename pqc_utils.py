import base64
import hashlib
import os

# =====================================================
# KYBER PQC (Real or Simulated)
# =====================================================

try:
    from pqcrypto.kem.kyber512 import (
        generate_keypair as kyber_generate,
        encrypt as kyber_encaps,
        decrypt as kyber_decaps
    )
    _HAS_KYBER = True
except Exception:
    _HAS_KYBER = False

# =====================================================
# FRODOKEM PQC (Real or Simulated)
# =====================================================

try:
    from pqcrypto.kem.frodokem640aes import (
        generate_keypair as frodo_generate,
        encrypt as frodo_encaps,
        decrypt as frodo_decaps
    )
    _HAS_FRODO = True
except Exception:
    _HAS_FRODO = False

# =====================================================
# SIMULATION CONSTANTS
# =====================================================

SIMULATED_KYBER_SECRET = hashlib.sha256(
    b"simulated_kyber_shared_secret"
).digest()[:32]

SIMULATED_FRODO_SECRET = hashlib.sha256(
    b"simulated_frodo_shared_secret"
).digest()[:32]

# =====================================================
# BASE64 HELPERS
# =====================================================

def b64_encode(b: bytes) -> str:
    return base64.b64encode(b).decode()

def b64_decode(s: str) -> bytes:
    return base64.b64decode(s.encode())

# =====================================================
# KYBER FUNCTIONS
# =====================================================

def generate_kyber_keypair():
    if _HAS_KYBER:
        pk, sk = kyber_generate()
        return bytes(pk), bytes(sk)
    else:
        return os.urandom(800), os.urandom(1632)

def kyber_encapsulate_with_pk(public_key: bytes):
    if _HAS_KYBER:
        ct, ss = kyber_encaps(public_key)
        return bytes(ct), bytes(ss)
    else:
        return os.urandom(768), SIMULATED_KYBER_SECRET

def kyber_decapsulate_with_sk(secret_key: bytes, ciphertext: bytes):
    if _HAS_KYBER:
        ss = kyber_decaps(secret_key, ciphertext)
        return bytes(ss)
    else:
        return SIMULATED_KYBER_SECRET

# =====================================================
# FRODOKEM FUNCTIONS
# =====================================================

def generate_frodo_keypair():
    if _HAS_FRODO:
        pk, sk = frodo_generate()
        return bytes(pk), bytes(sk)
    else:
        return os.urandom(9600), os.urandom(19888)

def frodo_encapsulate_with_pk(public_key: bytes):
    if _HAS_FRODO:
        ct, ss = frodo_encaps(public_key)
        return bytes(ct), bytes(ss)
    else:
        return os.urandom(9720), SIMULATED_FRODO_SECRET

def frodo_decapsulate_with_sk(secret_key: bytes, ciphertext: bytes):
    if _HAS_FRODO:
        ss = frodo_decaps(secret_key, ciphertext)
        return bytes(ss)
    else:
        return SIMULATED_FRODO_SECRET

# =====================================================
# PQC ALGORITHM AGILITY (CORE FEATURE)
# =====================================================

def generate_pqc_keypair(algorithm="kyber"):
    if algorithm == "kyber":
        return generate_kyber_keypair()
    elif algorithm == "frodo":
        return generate_frodo_keypair()
    else:
        raise ValueError("Unsupported PQC algorithm")

def pqc_encapsulate(public_key: bytes, algorithm="kyber"):
    if algorithm == "kyber":
        return kyber_encapsulate_with_pk(public_key)
    elif algorithm == "frodo":
        return frodo_encapsulate_with_pk(public_key)
    else:
        raise ValueError("Unsupported PQC algorithm")

def pqc_decapsulate(secret_key: bytes, ciphertext: bytes, algorithm="kyber"):
    if algorithm == "kyber":
        return kyber_decapsulate_with_sk(secret_key, ciphertext)
    elif algorithm == "frodo":
        return frodo_decapsulate_with_sk(secret_key, ciphertext)
    else:
        raise ValueError("Unsupported PQC algorithm")

# =====================================================
# HYBRID QKD + PQC AES-256 KEY DERIVATION
# =====================================================

def derive_hybrid_aes_key(qkd_aes_bytes: bytes, pqc_shared_secret: bytes) -> bytes:
    """
    Generates a 32-byte AES-256 key using QKD + PQC hybridization.
    """

    h_qkd = hashlib.sha256(qkd_aes_bytes).digest()
    h_pqc = hashlib.sha256(pqc_shared_secret).digest()

    hybrid_key = bytes(h_qkd[i] ^ h_pqc[i] for i in range(32))

    return hybrid_key
