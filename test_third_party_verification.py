from third_party_verification import verify_server_certificate

result = verify_server_certificate(
    server_cert_path="certs/server/server.crt",
    ca_cert_path="certs/ca/ca.crt"
)

print("Trust Established:", result)
