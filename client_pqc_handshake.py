from pqc_utils import pqc_encapsulate
from dilithium_utils import dilithium_verify_signature

# ---------------- CLIENT SIDE ----------------

def client_verify_and_encapsulate(handshake_data):
    pqc_pk = handshake_data["pqc_public_key"]
    dil_pk = handshake_data["dilithium_public_key"]
    signature = handshake_data["signature"]
    algo = handshake_data["pqc_algorithm"]

    # VERIFY SIGNATURE FIRST
    is_valid = dilithium_verify_signature(
        dil_pk,
        pqc_pk,
        signature
    )

    if not is_valid:
        raise Exception("❌ Invalid PQC public key signature")

    print("✅ PQC Public Key Verified")

    # Safe to encapsulate now
    ciphertext, shared_secret = pqc_encapsulate(pqc_pk, algo)

    return ciphertext, shared_secret
