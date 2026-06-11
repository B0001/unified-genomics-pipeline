"""Regression tests for auth.ga4gh_passport and auth.federated."""
from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))

from auth.ga4gh_passport import create_client, get_object
from auth.federated import resolve_federated_uri


# ---------------------------------------------------------------------------
# create_client
# ---------------------------------------------------------------------------

class TestCreateClient:
    def test_returns_client_built_with_url_and_jwt(self, mock_drs_url, mock_jwt):
        fake_client = MagicMock()
        with patch("auth.ga4gh_passport.tes_client") as mock_tes:
            mock_tes.Client.return_value = fake_client
            result = create_client(url=mock_drs_url, jwt=mock_jwt)
        mock_tes.Client.assert_called_once_with(url=mock_drs_url, jwt=mock_jwt)
        assert result is fake_client

    def test_empty_url_raises_value_error(self, mock_jwt):
        with pytest.raises(ValueError, match="URL"):
            create_client(url="", jwt=mock_jwt)

    def test_empty_jwt_raises_value_error(self, mock_drs_url):
        with pytest.raises(ValueError, match="JWT"):
            create_client(url=mock_drs_url, jwt="")

    def test_both_empty_raises_on_url_first(self):
        with pytest.raises(ValueError, match="URL"):
            create_client(url="", jwt="")

    def test_whitespace_only_url_not_accepted(self, mock_jwt):
        # Falsy string check catches whitespace-only strings
        with pytest.raises(ValueError):
            create_client(url="   ", jwt=mock_jwt)

    def test_whitespace_only_jwt_not_accepted(self, mock_drs_url):
        with pytest.raises(ValueError):
            create_client(url=mock_drs_url, jwt="   ")


# ---------------------------------------------------------------------------
# get_object
# ---------------------------------------------------------------------------

class TestGetObject:
    def test_returns_drs_object_from_client(self, mock_drs_client, mock_drs_object):
        result = get_object(mock_drs_client, "a001")
        assert result is mock_drs_object

    def test_calls_get_object_with_correct_id(self, mock_drs_client):
        get_object(mock_drs_client, "dataset-XYZ")
        mock_drs_client.GetObject.assert_called_once_with("dataset-XYZ")

    def test_propagates_connection_error(self):
        client = MagicMock()
        client.GetObject.side_effect = ConnectionError("DRS node unreachable")
        with pytest.raises(ConnectionError, match="unreachable"):
            get_object(client, "a001")

    def test_propagates_key_error_on_bad_id(self):
        client = MagicMock()
        client.GetObject.side_effect = KeyError("not found")
        with pytest.raises(KeyError):
            get_object(client, "nonexistent-id")


# ---------------------------------------------------------------------------
# resolve_federated_uri
# ---------------------------------------------------------------------------

class TestResolveFederatedUri:
    def test_returns_cloud_uri_string(self, mock_drs_url, mock_jwt, mock_drs_object):
        with patch("auth.federated.create_client") as mock_create:
            client = MagicMock()
            client.GetObject.return_value = mock_drs_object
            mock_create.return_value = client

            result = resolve_federated_uri(mock_drs_url, mock_jwt, "a001")

        assert result == mock_drs_object.access_methods.access_url.url

    def test_passes_url_and_jwt_to_create_client(self, mock_drs_url, mock_jwt, mock_drs_object):
        with patch("auth.federated.create_client") as mock_create:
            client = MagicMock()
            client.GetObject.return_value = mock_drs_object
            mock_create.return_value = client

            resolve_federated_uri(mock_drs_url, mock_jwt, "a001")

        mock_create.assert_called_once_with(url=mock_drs_url, jwt=mock_jwt)

    def test_calls_get_object_with_correct_id(self, mock_drs_url, mock_jwt, mock_drs_object):
        with patch("auth.federated.create_client") as mock_create:
            client = MagicMock()
            client.GetObject.return_value = mock_drs_object
            mock_create.return_value = client

            resolve_federated_uri(mock_drs_url, mock_jwt, "custom-id-99")

        client.GetObject.assert_called_once_with("custom-id-99")

    def test_different_uris_are_returned_correctly(self, mock_drs_url, mock_jwt):
        for uri in ["s3://bucket/a.vcf", "gs://ref/b.bed", "az://store/c.bam"]:
            obj = MagicMock()
            obj.access_methods.access_url.url = uri
            with patch("auth.federated.create_client") as mock_create:
                c = MagicMock()
                c.GetObject.return_value = obj
                mock_create.return_value = c
                result = resolve_federated_uri(mock_drs_url, mock_jwt, "x")
            assert result == uri
