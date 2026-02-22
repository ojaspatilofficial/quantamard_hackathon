from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def load_certificate(cert_path):
    """
    Tries to load certificate as PEM first, then DER
    """
    with open(cert_path, "rb") as f:
        cert_data = f.read()

    try:
        # Try PEM
        return x509.load_pem_x509_certificate(cert_data, default_backend())
    except ValueError:
        # Fallback to DER
        return x509.load_der_x509_certificate(cert_data, default_backend())


def verify_server_certificate(server_cert_path, ca_cert_path):
    """
    Verifies server certificate using CA certificate
    (Third-party trust verification)
    """

    # Load certificates
    ca_cert = load_certificate(ca_cert_path)
    server_cert = load_certificate(server_cert_path)

    # Get CA public key
    ca_public_key = ca_cert.public_key()

    try:
        # Verify signature on server cert
        ca_public_key.verify(
            server_cert.signature,
            server_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            server_cert.signature_hash_algorithm,
        )

        print("✅ Server certificate verified by trusted CA")
        return True

    except Exception as e:
        print("❌ Certificate verification failed:", e)
        return False
