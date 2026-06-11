import tes_client
# Initialize the client with your GA4GH Passport JWT
client = tes_client.Client(
    url="https://path.to.biobank/ga4gh/drs/v1/",
    jwt="YOUR_SECURE_JWT_TOKEN"
)
# Access the data object securely
response = client.GetObject("a001")