"""Regression tests for server.flight_server."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))

import polars_bio as pb
import pyarrow.flight as flight_stub

from server.flight_server import GenomicFlightServer, start_server


def _make_ticket(dataset_id: str) -> MagicMock:
    ticket = MagicMock()
    ticket.ticket = dataset_id.encode("utf-8")
    return ticket


# ---------------------------------------------------------------------------
# GenomicFlightServer.do_get
# ---------------------------------------------------------------------------

class TestDoGet:
    def test_decodes_ticket_to_dataset_id(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        server = GenomicFlightServer.__new__(GenomicFlightServer)
        server.do_get(MagicMock(), _make_ticket("patient-001"))
        pb.read_vcf.assert_called_with("patient-001.vcf")

    def test_appends_dot_vcf_extension(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        server = GenomicFlightServer.__new__(GenomicFlightServer)
        server.do_get(MagicMock(), _make_ticket("cohort-XYZ"))
        pb.read_vcf.assert_called_with("cohort-XYZ.vcf")

    def test_returns_record_batch_stream(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        flight_stub.RecordBatchStream.reset_mock()
        server = GenomicFlightServer.__new__(GenomicFlightServer)
        server.do_get(MagicMock(), _make_ticket("ds1"))
        flight_stub.RecordBatchStream.assert_called_once_with(
            mock_polars_df.to_arrow.return_value
        )

    def test_calls_to_arrow_on_dataframe(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        mock_polars_df.to_arrow.reset_mock()
        server = GenomicFlightServer.__new__(GenomicFlightServer)
        server.do_get(MagicMock(), _make_ticket("ds1"))
        mock_polars_df.to_arrow.assert_called_once()

    def test_raises_flight_server_error_on_missing_dataset(self):
        pb.read_vcf.side_effect = FileNotFoundError("file not found")
        server = GenomicFlightServer.__new__(GenomicFlightServer)
        with pytest.raises(flight_stub.FlightServerError):
            server.do_get(MagicMock(), _make_ticket("no-such-dataset"))
        pb.read_vcf.side_effect = None  # reset

    def test_flight_error_message_contains_dataset_id(self):
        pb.read_vcf.side_effect = FileNotFoundError("missing")
        server = GenomicFlightServer.__new__(GenomicFlightServer)
        with pytest.raises(flight_stub.FlightServerError, match="bad-id"):
            server.do_get(MagicMock(), _make_ticket("bad-id"))
        pb.read_vcf.side_effect = None

    def test_handles_utf8_dataset_ids_with_hyphens(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        server = GenomicFlightServer.__new__(GenomicFlightServer)
        server.do_get(MagicMock(), _make_ticket("cohort-2024-01-uk-biobank"))
        pb.read_vcf.assert_called_with("cohort-2024-01-uk-biobank.vcf")


# ---------------------------------------------------------------------------
# start_server
# ---------------------------------------------------------------------------

class TestStartServer:
    def test_constructs_server_with_combined_uri(self):
        with patch("server.flight_server.GenomicFlightServer") as MockServer:
            instance = MagicMock()
            MockServer.return_value = instance
            start_server(host="grpc://0.0.0.0", port=8815)
            MockServer.assert_called_once_with("grpc://0.0.0.0:8815")

    def test_calls_serve_on_the_instance(self):
        with patch("server.flight_server.GenomicFlightServer") as MockServer:
            instance = MagicMock()
            MockServer.return_value = instance
            start_server()
            instance.serve.assert_called_once()

    def test_returns_server_instance(self):
        with patch("server.flight_server.GenomicFlightServer") as MockServer:
            instance = MagicMock()
            MockServer.return_value = instance
            result = start_server()
            assert result is instance

    def test_custom_host_and_port_forwarded(self):
        with patch("server.flight_server.GenomicFlightServer") as MockServer:
            instance = MagicMock()
            MockServer.return_value = instance
            start_server(host="grpc://192.168.1.1", port=9999)
            MockServer.assert_called_once_with("grpc://192.168.1.1:9999")
