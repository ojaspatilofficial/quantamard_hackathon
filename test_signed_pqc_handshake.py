from server_pqc_handshake import server_prepare_pqc_handshake
from client_pqc_handshake import client_verify_and_encapsulate
from pqc_utils import pqc_decapsulate

# SERVER prepares handshake
handshake = server_prepare_pqc_handshake("kyber")

# CLIENT verifies + encapsulates
ciphertext, client_secret = client_verify_and_encapsulate(handshake)

# SERVER decapsulates
server_secret = pqc_decapsulate(
    handshake["pqc_secret_key"],
    ciphertext,
    handshake["pqc_algorithm"]
)

print("Shared Secret Match:", client_secret == server_secret)
