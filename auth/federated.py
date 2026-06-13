from __future__ import annotations
from auth.ga4gh_passport import create_client

def resolve_federated_uri(url: str, jwt: str, object_id: str) -> str:
    client = create_client(url=url, jwt=jwt)
    response = client.GetObject(object_id)
    return response.access_methods.access_url.url
