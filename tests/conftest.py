"""Shared pytest fixtures and external-dependency stubs for the gene test suite.

All heavy bioinformatics libraries (polars_bio, scanpy, rapids_singlecell,
crypt4gh, tes_client, pyarrow, torch, transformers, dask, rmm) are stubbed
out at the *module* level here so that every test file can import the
production source code without requiring GPU hardware or specialised packages.
"""
from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Stub external packages (must happen before any production imports)
# ---------------------------------------------------------------------------

def _make_stub(name: str, **attrs) -> types.ModuleType:
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


def _register_stub(name: str, **attrs) -> types.ModuleType:
    mod = _make_stub(name, **attrs)
    sys.modules.setdefault(name, mod)
    return mod


# tes_client
_register_stub("tes_client", Client=MagicMock())

# polars (lightweight, usually available; stub anyway for isolation)
_polars_stub = _register_stub("polars", col=MagicMock())

# polars_bio
_pb_expr = _make_stub("polars_bio.expr", vep_consequence=MagicMock(return_value=MagicMock()))
_register_stub("polars_bio", read_vcf=MagicMock(), read_bed=MagicMock(),
               overlap=MagicMock(), nearest=MagicMock(), expr=_pb_expr)
sys.modules.setdefault("polars_bio.expr", _pb_expr)

# scanpy
_register_stub("scanpy", read_h5ad=MagicMock())

# rapids_singlecell
_rsc_pp = _make_stub("rapids_singlecell.pp", normalize_total=MagicMock(),
                      log1p=MagicMock(), pca=MagicMock(), neighbors=MagicMock())
_rsc_tl = _make_stub("rapids_singlecell.tl", leiden=MagicMock())
_rsc = _register_stub("rapids_singlecell", pp=_rsc_pp, tl=_rsc_tl)
sys.modules.setdefault("rapids_singlecell.pp", _rsc_pp)
sys.modules.setdefault("rapids_singlecell.tl", _rsc_tl)

# crypt4gh
_c4gh_keys = _make_stub("crypt4gh.keys",
                         get_private_key=MagicMock(return_value=b"private"),
                         get_public_key=MagicMock(return_value=b"public"))
_c4gh_lib = _make_stub("crypt4gh.lib", encrypt=MagicMock(), decrypt=MagicMock())
_register_stub("crypt4gh")
sys.modules.setdefault("crypt4gh.keys", _c4gh_keys)
sys.modules.setdefault("crypt4gh.lib", _c4gh_lib)

# pyarrow / pyarrow.flight
_flight_stub = _make_stub(
    "pyarrow.flight",
    FlightServerBase=object,
    RecordBatchStream=MagicMock(),
    FlightServerError=type("FlightServerError", (Exception,), {}),
    Ticket=MagicMock(),
)
_register_stub("pyarrow")
sys.modules.setdefault("pyarrow.flight", _flight_stub)

# torch
_torch_no_grad = MagicMock()
_torch_no_grad.return_value.__enter__ = lambda s: s
_torch_no_grad.return_value.__exit__ = MagicMock(return_value=False)
_register_stub("torch", no_grad=_torch_no_grad, Tensor=MagicMock())

# transformers
_register_stub("transformers",
               AutoModelForMaskedLM=MagicMock(),
               AutoTokenizer=MagicMock())

# dask.distributed
_register_stub("dask")
_register_stub("dask.distributed", Client=MagicMock())

# rmm / rmm.allocators.dask
_register_stub("rmm")
_register_stub("rmm.allocators")
_register_stub("rmm.allocators.dask", initialising_rmm=MagicMock())


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

MOCK_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig"
MOCK_DRS_URL = "http://localhost:9101/ga4gh/drs/v1/"
MOCK_CLOUD_URI = "s3://biobank-bucket/cohort-A001/data.vcf.gz"
MOCK_OBJECT_ID = "a001"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_jwt() -> str:
    return MOCK_JWT


@pytest.fixture
def mock_drs_url() -> str:
    return MOCK_DRS_URL


@pytest.fixture
def mock_drs_object() -> MagicMock:
    obj = MagicMock()
    obj.access_methods.access_url.url = MOCK_CLOUD_URI
    return obj


@pytest.fixture
def mock_drs_client(mock_drs_object) -> MagicMock:
    client = MagicMock()
    client.GetObject.return_value = mock_drs_object
    return client


@pytest.fixture
def mock_polars_df() -> MagicMock:
    df = MagicMock()
    df.head.return_value = df
    df.with_columns.return_value = df
    df.to_arrow.return_value = MagicMock()
    return df


@pytest.fixture
def mock_adata() -> MagicMock:
    adata = MagicMock()
    adata.obs = {"leiden": MagicMock()}
    adata.obs["leiden"].value_counts.return_value = {"0": 1000, "1": 500}
    return adata


@pytest.fixture
def tmp_plaintext_file(tmp_path) -> str:
    """A small in-memory FASTQ file for encryption tests."""
    p = tmp_path / "patient_data.fastq"
    p.write_bytes(b"@SEQ_ID\nGATTACA\n+\nIIIIIII\n")
    return str(p)


@pytest.fixture
def tmp_encrypted_path(tmp_path) -> str:
    return str(tmp_path / "patient_data.fastq.c4gh")


@pytest.fixture
def tmp_decrypted_path(tmp_path) -> str:
    return str(tmp_path / "patient_data.fastq.dec")
