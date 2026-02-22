import time
from pqc_utils import generate_pqc_keypair, pqc_encapsulate, pqc_decapsulate

def test_algorithm(algo):
    print(f"\n=== Testing {algo.upper()} ===")

    # Key generation
    start = time.time()
    pk, sk = generate_pqc_keypair(algo)
    keygen_time = time.time() - start

    # Encapsulation
    start = time.time()
    ct, client_secret = pqc_encapsulate(pk, algo)
    encap_time = time.time() - start

    # Decapsulation
    start = time.time()
    server_secret = pqc_decapsulate(sk, ct, algo)
    decap_time = time.time() - start

    print("Public Key Size :", len(pk), "bytes")
    print("Ciphertext Size:", len(ct), "bytes")
    print("Keygen Time    :", round(keygen_time, 4), "seconds")
    print("Encap Time     :", round(encap_time, 4), "seconds")
    print("Decap Time     :", round(decap_time, 4), "seconds")
    print("Shared Secret Match:", client_secret == server_secret)


if __name__ == "__main__":
    test_algorithm("kyber")
    test_algorithm("frodo")
