"""Regression tests for drs.resolution."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))

from drs.resolution import get_access_methods, resolve_cloud_uri


CLOUD_URI = "s3://biobank/cohort.vcf.gz"


# ---------------------------------------------------------------------------
# resolve_cloud_uri
# ---------------------------------------------------------------------------

class TestResolveCloudUri:
    def test_returns_uri_string(self, mock_drs_client, mock_drs_object):
        mock_drs_object.access_methods.access_url.url = CLOUD_URI
        result = resolve_cloud_uri(mock_drs_client, "a001")
        assert result == CLOUD_URI

    def test_calls_get_object_once(self, mock_drs_client):
        resolve_cloud_uri(mock_drs_client, "a001")
        mock_drs_client.GetObject.assert_called_once_with("a001")

    def test_passes_object_id_verbatim(self, mock_drs_client):
        resolve_cloud_uri(mock_drs_client, "dataset-99-XYZ")
        mock_drs_client.GetObject.assert_called_with("dataset-99-XYZ")

    def test_raises_attribute_error_on_missing_access_methods(self):
        bad_obj = MagicMock(spec=[])          # no attributes at all
        client = MagicMock()
        client.GetObject.return_value = bad_obj
        with pytest.raises(AttributeError):
            resolve_cloud_uri(client, "a001")

    def test_propagates_network_error(self):
        client = MagicMock()
        client.GetObject.side_effect = TimeoutError("gateway timeout")
        with pytest.raises(TimeoutError):
            resolve_cloud_uri(client, "a001")

    @pytest.mark.parametrize("uri", [
        "s3://bucket/variants.vcf.gz",
        "gs://ref-data/genes.bed",
        "az://cold-store/archive.cram",
    ])
    def test_returns_various_cloud_uri_schemes(self, uri):
        obj = MagicMock()
        obj.access_methods.access_url.url = uri
        client = MagicMock()
        client.GetObject.return_value = obj
        assert resolve_cloud_uri(client, "x") == uri


# ---------------------------------------------------------------------------
# get_access_methods
# ---------------------------------------------------------------------------

class TestGetAccessMethods:
    def test_returns_access_methods_payload(self, mock_drs_client, mock_drs_object):
        result = get_access_methods(mock_drs_client, "a001")
        # Should be the .access_methods attribute of the returned DRS object
        assert result is mock_drs_object.access_methods

    def test_calls_get_object_with_correct_id(self, mock_drs_client):
        get_access_methods(mock_drs_client, "cohort-B002")
        mock_drs_client.GetObject.assert_called_once_with("cohort-B002")

    def test_does_not_call_get_object_twice(self, mock_drs_client):
        get_access_methods(mock_drs_client, "a001")
        assert mock_drs_client.GetObject.call_count == 1
