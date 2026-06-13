from __future__ import annotations
import sys, types
from unittest.mock import MagicMock
import pytest

def _stub(name, **attrs):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod

_stub("tes_client", Client=MagicMock())

_pbe = _stub("polars_bio.expr", vep_consequence=MagicMock(return_value=MagicMock()))
_stub("polars_bio", read_vcf=MagicMock(), read_bed=MagicMock(),
      overlap=MagicMock(), nearest=MagicMock(), expr=_pbe)
_stub("polars", col=MagicMock())
_stub("scanpy", read_h5ad=MagicMock())

_pp = _stub("rapids_singlecell.pp", normalize_total=MagicMock(), log1p=MagicMock(),
            pca=MagicMock(), neighbors=MagicMock())
_tl = _stub("rapids_singlecell.tl", leiden=MagicMock())
_stub("rapids_singlecell", pp=_pp, tl=_tl)

_c4k = _stub("crypt4gh.keys",
             get_private_key=MagicMock(return_value=b"private"),
             get_public_key=MagicMock(return_value=b"public"))
_c4l = _stub("crypt4gh.lib", encrypt=MagicMock(), decrypt=MagicMock())
_stub("crypt4gh", keys=_c4k, lib=_c4l)

_fse = type("FlightServerError", (Exception,), {})
_fl  = _stub("pyarrow.flight", FlightServerBase=object,
             RecordBatchStream=MagicMock(), FlightServerError=_fse, Ticket=MagicMock())
_stub("pyarrow", flight=_fl)

_ng = MagicMock()
_ng.return_value.__enter__ = lambda s: s
_ng.return_value.__exit__  = MagicMock(return_value=False)
_stub("torch", no_grad=_ng, Tensor=MagicMock())
_stub("transformers", AutoModelForMaskedLM=MagicMock(), AutoTokenizer=MagicMock())

_stub("dask")
_stub("dask.distributed", Client=MagicMock())
_stub("rmm"); _stub("rmm.allocators")
_stub("rmm.allocators.dask", initialising_rmm=MagicMock())

MOCK_JWT      = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig"
MOCK_DRS_URL  = "http://localhost:9101/ga4gh/drs/v1/"
MOCK_CLOUD_URI = "s3://biobank-bucket/cohort-A001/data.vcf.gz"

@pytest.fixture
def mock_jwt():        return MOCK_JWT
@pytest.fixture
def mock_drs_url():    return MOCK_DRS_URL

@pytest.fixture
def mock_drs_object():
    obj = MagicMock()
    obj.access_methods.access_url.url = MOCK_CLOUD_URI
    return obj

@pytest.fixture
def mock_drs_client(mock_drs_object):
    c = MagicMock(); c.GetObject.return_value = mock_drs_object; return c

@pytest.fixture
def mock_polars_df():
    df = MagicMock()
    df.head.return_value = df
    df.with_columns.return_value = df
    df.to_arrow.return_value = MagicMock()
    return df

@pytest.fixture
def mock_adata():
    a = MagicMock()
    leiden = MagicMock(); leiden.value_counts.return_value = {"0": 1000, "1": 500}
    seqs   = MagicMock(); seqs.tolist.return_value = ["ATCG", "GCTA"]
    a.obs  = {"leiden": leiden, "cell_sequences": seqs}
    return a

@pytest.fixture
def tmp_plaintext_file(tmp_path):
    p = tmp_path / "patient_data.fastq"
    p.write_bytes(b"@SEQ_ID\nGATTACA\n+\nIIIIIII\n")
    return str(p)

@pytest.fixture
def tmp_encrypted_path(tmp_path): return str(tmp_path / "patient_data.fastq.c4gh")
@pytest.fixture
def tmp_decrypted_path(tmp_path): return str(tmp_path / "patient_data.fastq.dec")
