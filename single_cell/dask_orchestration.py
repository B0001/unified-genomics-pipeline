import scanpy as sc
import rapids_singlecell as rsc
from dask.distributed import Client
from rmm.allocators.dask import initialising_rmm

# Initialize a Dask cluster across multiple GPUs
client = Client(scheduler_file="scheduler.json")

# Configure the RAPIDS Memory Manager (RMM)
# This enables automatic spilling to host memory, 
# allowing for the analysis of 100+ million cells.
client.run(initialising_rmm, managed_memory=True, pool_size="40GB")

# Load the massive matrix in backed mode (reading directly from disk)
adata = sc.read_h5ad("100_million_cells.h5ad", backed='r')

# The data is now ready to be processed by Dask-accelerated Transformers
# or distributed clustering algorithms without triggering out-of-memory errors.