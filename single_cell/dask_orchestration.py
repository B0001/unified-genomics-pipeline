from __future__ import annotations
import scanpy as sc
from dask.distributed import Client
from rmm.allocators.dask import initialising_rmm

def init_gpu_cluster(scheduler_file: str, pool_size: str = "40GB") -> Client:
    client = Client(scheduler_file=scheduler_file)
    client.run(initialising_rmm, managed_memory=True, pool_size=pool_size)
    return client

def load_backed_matrix(h5ad_path: str):
    return sc.read_h5ad(h5ad_path, backed="r")
