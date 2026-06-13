from __future__ import annotations
import tes_client

def create_client(url: str, jwt: str) -> tes_client.Client:
    if not url:
        raise ValueError("DRS endpoint URL must not be empty")
    if not jwt:
        raise ValueError("JWT token must not be empty")
    return tes_client.Client(url=url, jwt=jwt)

def get_object(client, object_id: str):
    return client.GetObject(object_id)
