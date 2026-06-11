import tes_client

# The JWT token (GA4GH Passport) is passed to securely authenticate
# against the Data Repository Service (DRS).
client = tes_client.Client(
    url="https://federated-node.org/ga4gh/drs/v1/",
    jwt="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # Secure Bearer Token
)

# Resolve the dataset ID to a native cloud URI securely
response = client.GetObject("a001")
print(f"Secure Cloud URI: {response.access_methods.access_url.url}")