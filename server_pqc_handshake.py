from pqc_utils import generate_pqc_keypair
from dilithium_utils import (
    generate_dilithium_keypair,
    dilithium_sign_message
)

# ---------------- SERVER SIDE ----------------

def server_prepare_pqc_handshake(pqc_algorithm="kyber"):
    # Generate PQC KEM keypair (Kyber / Frodo)
    pqc_public_key, pqc_secret_key = generate_pqc_keypair(pqc_algorithm)

    # Generate Dilithium signing keypair (server identity)
    dil_pk, dil_sk = generate_dilithium_keypair()

    # Sign the PQC public key
    signature = dilithium_sign_message(dil_sk, pqc_public_key)

    return {
        "pqc_algorithm": pqc_algorithm,
        "pqc_public_key": pqc_public_key,
        "pqc_secret_key": pqc_secret_key,   # keep private on server
        "dilithium_public_key": dil_pk,
        "signature": signature
    }
