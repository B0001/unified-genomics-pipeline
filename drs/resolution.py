from __future__ import annotations

def resolve_cloud_uri(client, object_id: str) -> str:
    drs_object = client.GetObject(object_id)
    return drs_object.access_methods.access_url.url

def get_access_methods(client, object_id: str):
    drs_object = client.GetObject(object_id)
    return drs_object.access_methods
