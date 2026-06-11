"""Integration test for a live (or local mock) DRS endpoint.

Previously: test_drs_connection.py

Run these against a real or local mock-DRS instance:

    pytest tests/integration/ -m integration --drs-url http://localhost:9101/ga4gh/drs/v1/ --jwt YOUR_TOKEN

Skipped automatically when neither ``--drs-url`` nor the ``DRS_URL`` env var
is set, so CI stays green without a running DRS node.
"""
from __future__ import annotations

import os

import pytest

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))


# ---------------------------------------------------------------------------
# CLI / env-var configuration
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    """Allow passing DRS coordinates on the command line."""
    parser.addoption("--drs-url", default=None, help="Live DRS endpoint URL")
    parser.addoption("--jwt", default=None, help="GA4GH Passport JWT token")


@pytest.fixture(scope="session")
def drs_url(request):
    url = request.config.getoption("--drs-url") or os.getenv("DRS_URL")
    if not url:
        pytest.skip("No DRS endpoint configured (set --drs-url or DRS_URL env var)")
    return url


@pytest.fixture(scope="session")
def drs_jwt(request):
    token = request.config.getoption("--jwt") or os.getenv("DRS_JWT", "YOUR_BEARER_TOKEN")
    return token


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDrsConnection:
    def test_can_resolve_known_object_id(self, drs_url, drs_jwt):
        """Connect to the DRS node and resolve object 'a001' to a cloud URI."""
        import tes_client
        from drs.resolution import resolve_cloud_uri

        client = tes_client.Client(url=drs_url, jwt=drs_jwt)
        uri = resolve_cloud_uri(client, "a001")

        assert isinstance(uri, str)
        assert uri.startswith(("s3://", "gs://", "az://", "http")), (
            f"Unexpected URI scheme: {uri}"
        )

    def test_resolved_uri_is_non_empty(self, drs_url, drs_jwt):
        import tes_client
        from drs.resolution import resolve_cloud_uri

        client = tes_client.Client(url=drs_url, jwt=drs_jwt)
        uri = resolve_cloud_uri(client, "a001")
        assert len(uri) > 0

    def test_access_methods_are_returned(self, drs_url, drs_jwt):
        import tes_client
        from drs.resolution import get_access_methods

        client = tes_client.Client(url=drs_url, jwt=drs_jwt)
        methods = get_access_methods(client, "a001")
        assert methods is not None
