from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime

# -------------------------------------------------
# Generate NEW CA private key
# -------------------------------------------------
ca_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Save CA private key
with open("ca.key", "wb") as f:
    f.write(
        ca_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

# -------------------------------------------------
# Build CA certificate
# -------------------------------------------------
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CryptexQ"),
    x509.NameAttribute(NameOID.COMMON_NAME, "CryptexQ Root CA"),
])

ca_cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(ca_private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    .add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    )
    .sign(ca_private_key, hashes.SHA256(), default_backend())
)

# Save CA certificate
with open("ca.crt", "wb") as f:
    f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

print("✅ CA private key and certificate generated successfully")
