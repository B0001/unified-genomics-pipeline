from __future__ import annotations
import scanpy as sc
import rapids_singlecell as rsc

def run_pipeline(h5ad_path: str, resolution: float = 1.0):
    adata = sc.read_h5ad(h5ad_path)
    rsc.pp.normalize_total(adata)
    rsc.pp.log1p(adata)
    rsc.pp.pca(adata)
    rsc.pp.neighbors(adata)
    rsc.tl.leiden(adata, resolution=resolution)
    return adata

def get_cluster_counts(adata):
    return adata.obs["leiden"].value_counts()
