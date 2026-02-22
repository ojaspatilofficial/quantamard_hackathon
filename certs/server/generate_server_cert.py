from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime
import ipaddress

# -------------------------------------------------
# Load CA private key and certificate
# -------------------------------------------------
with open("../ca/ca.key", "rb") as f:
    ca_private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

with open("../ca/ca.crt", "rb") as f:
    ca_cert = x509.load_pem_x509_certificate(
        f.read(),
        default_backend()
    )

# -------------------------------------------------
# Generate server private key
# -------------------------------------------------
server_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

with open("server.key", "wb") as f:
    f.write(
        server_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

# -------------------------------------------------
# Build server certificate (signed by CA)
# -------------------------------------------------
subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CryptexQ"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])

# Add Subject Alternative Names for localhost
san = x509.SubjectAlternativeName([
    x509.DNSName("localhost"),
    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    x509.IPAddress(ipaddress.IPv6Address("::1")),
])

server_cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(ca_cert.subject)
    .public_key(server_private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    .add_extension(
        san,
        critical=False,
    )
    .add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    .add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
        ]),
        critical=True,
    )
    .sign(ca_private_key, hashes.SHA256(), default_backend())
)

with open("server.crt", "wb") as f:
    f.write(server_cert.public_bytes(serialization.Encoding.PEM))

print("✅ Server certificate generated and signed by CA")
