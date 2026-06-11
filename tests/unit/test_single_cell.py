"""Regression tests for single_cell.gpu_analysis, dask_orchestration, and foundation_model."""
from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))

import scanpy as sc
import rapids_singlecell as rsc

from single_cell.gpu_analysis import get_cluster_counts, run_pipeline
from single_cell.dask_orchestration import init_gpu_cluster, load_backed_matrix
from single_cell.foundation_model import embed_cells, load_model


# ---------------------------------------------------------------------------
# run_pipeline (gpu_analysis)
# ---------------------------------------------------------------------------

class TestRunPipeline:
    def test_reads_h5ad_from_given_path(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        run_pipeline("million_cells.h5ad")
        sc.read_h5ad.assert_called_with("million_cells.h5ad")

    def test_normalize_total_is_called(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        rsc.pp.normalize_total.reset_mock()
        run_pipeline("cells.h5ad")
        rsc.pp.normalize_total.assert_called_once_with(mock_adata)

    def test_log1p_is_called_after_normalize(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        rsc.pp.normalize_total.reset_mock()
        rsc.pp.log1p.reset_mock()
        run_pipeline("cells.h5ad")
        rsc.pp.log1p.assert_called_once_with(mock_adata)

    def test_pca_is_called(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        rsc.pp.pca.reset_mock()
        run_pipeline("cells.h5ad")
        rsc.pp.pca.assert_called_once_with(mock_adata)

    def test_neighbors_is_called(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        rsc.pp.neighbors.reset_mock()
        run_pipeline("cells.h5ad")
        rsc.pp.neighbors.assert_called_once_with(mock_adata)

    def test_leiden_is_called_with_correct_resolution(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        rsc.tl.leiden.reset_mock()
        run_pipeline("cells.h5ad", resolution=0.5)
        rsc.tl.leiden.assert_called_once_with(mock_adata, resolution=0.5)

    def test_default_resolution_is_one(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        rsc.tl.leiden.reset_mock()
        run_pipeline("cells.h5ad")
        _, kwargs = rsc.tl.leiden.call_args
        assert kwargs.get("resolution") == 1.0

    def test_returns_annotated_adata(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        result = run_pipeline("cells.h5ad")
        assert result is mock_adata


# ---------------------------------------------------------------------------
# get_cluster_counts
# ---------------------------------------------------------------------------

class TestGetClusterCounts:
    def test_returns_value_counts_of_leiden_column(self, mock_adata):
        result = get_cluster_counts(mock_adata)
        mock_adata.obs["leiden"].value_counts.assert_called_once()
        assert result is mock_adata.obs["leiden"].value_counts.return_value

    def test_raises_key_error_for_missing_leiden_column(self):
        adata = MagicMock()
        adata.obs = {}          # no 'leiden' key
        with pytest.raises(KeyError):
            get_cluster_counts(adata)


# ---------------------------------------------------------------------------
# init_gpu_cluster (dask_orchestration)
# ---------------------------------------------------------------------------

class TestInitGpuCluster:
    def test_creates_dask_client_from_scheduler_file(self):
        from dask.distributed import Client as DaskClient
        DaskClient.reset_mock()
        from rmm.allocators.dask import initialising_rmm
        init_gpu_cluster("scheduler.json")
        DaskClient.assert_called_once_with(scheduler_file="scheduler.json")

    def test_calls_client_run_with_rmm(self):
        from dask.distributed import Client as DaskClient
        mock_client = MagicMock()
        DaskClient.return_value = mock_client
        from rmm.allocators.dask import initialising_rmm
        init_gpu_cluster("scheduler.json", pool_size="32GB")
        mock_client.run.assert_called_once_with(
            initialising_rmm, managed_memory=True, pool_size="32GB"
        )

    def test_returns_dask_client(self):
        from dask.distributed import Client as DaskClient
        mock_client = MagicMock()
        DaskClient.return_value = mock_client
        result = init_gpu_cluster("scheduler.json")
        assert result is mock_client

    def test_default_pool_size_is_40gb(self):
        from dask.distributed import Client as DaskClient
        mock_client = MagicMock()
        DaskClient.return_value = mock_client
        from rmm.allocators.dask import initialising_rmm
        init_gpu_cluster("scheduler.json")
        _, kwargs = mock_client.run.call_args
        assert kwargs["pool_size"] == "40GB"


# ---------------------------------------------------------------------------
# load_backed_matrix (dask_orchestration)
# ---------------------------------------------------------------------------

class TestLoadBackedMatrix:
    def test_reads_h5ad_in_backed_mode(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        result = load_backed_matrix("100m_cells.h5ad")
        sc.read_h5ad.assert_called_with("100m_cells.h5ad", backed="r")
        assert result is mock_adata

    def test_uses_read_only_backed_mode(self):
        sc.read_h5ad.reset_mock()
        load_backed_matrix("data.h5ad")
        _, kwargs = sc.read_h5ad.call_args
        assert kwargs.get("backed") == "r"


# ---------------------------------------------------------------------------
# load_model (foundation_model)
# ---------------------------------------------------------------------------

class TestLoadModel:
    def test_loads_tokenizer_and_model(self):
        from transformers import AutoModelForMaskedLM, AutoTokenizer
        AutoTokenizer.from_pretrained.reset_mock()
        AutoModelForMaskedLM.from_pretrained.reset_mock()

        load_model("bio-transformer-scRNA", device="cpu")

        AutoTokenizer.from_pretrained.assert_called_once_with("bio-transformer-scRNA")
        AutoModelForMaskedLM.from_pretrained.assert_called_once_with("bio-transformer-scRNA")

    def test_returns_tokenizer_and_model_tuple(self):
        from transformers import AutoModelForMaskedLM, AutoTokenizer
        tok = MagicMock()
        mdl = MagicMock()
        AutoTokenizer.from_pretrained.return_value = tok
        AutoModelForMaskedLM.from_pretrained.return_value = mdl

        result = load_model("bio-transformer-scRNA", device="cpu")
        assert result[0] is tok

    def test_moves_model_to_device(self):
        from transformers import AutoModelForMaskedLM
        mdl = MagicMock()
        AutoModelForMaskedLM.from_pretrained.return_value = mdl
        load_model("bio-transformer-scRNA", device="cuda")
        mdl.to.assert_called_once_with("cuda")


# ---------------------------------------------------------------------------
# embed_cells (foundation_model)
# ---------------------------------------------------------------------------

class TestEmbedCells:
    def test_reads_h5ad_in_backed_mode(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        tok, mdl = MagicMock(), MagicMock()
        mdl.return_value.last_hidden_state = MagicMock()
        embed_cells("cells.h5ad", tok, mdl, device="cpu")
        sc.read_h5ad.assert_called_with("cells.h5ad", backed="r")

    def test_tokenizes_cell_sequences(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        tok = MagicMock()
        mdl = MagicMock()
        mdl.return_value.last_hidden_state = MagicMock()
        tok.return_value.to = MagicMock(return_value=tok.return_value)

        embed_cells("cells.h5ad", tok, mdl, device="cpu")

        tok.assert_called_once_with(
            mock_adata.obs["cell_sequences"].tolist(),
            return_tensors="pt",
        )

    def test_returns_last_hidden_state(self, mock_adata):
        sc.read_h5ad.return_value = mock_adata
        tok = MagicMock()
        tok.return_value.to = MagicMock(return_value=tok.return_value)
        expected = MagicMock(name="embeddings")
        mdl = MagicMock()
        mdl.return_value.last_hidden_state = expected

        result = embed_cells("cells.h5ad", tok, mdl, device="cpu")
        assert result is expected
