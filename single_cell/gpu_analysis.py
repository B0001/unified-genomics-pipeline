import scanpy as sc
import rapids_singlecell as rsc

# Load a massive, sparse single-cell transcriptomic matrix
adata = sc.read_h5ad("million_cells_matrix.h5ad")

# Offload the preprocessing and dimensionality reduction to the GPU
rsc.pp.normalize_total(adata)
rsc.pp.log1p(adata)
rsc.pp.pca(adata)

# Compute the nearest neighbor graph on the GPU
rsc.pp.neighbors(adata)

# Execute the Leiden algorithm to optimize modularity and discover cell types
# This runs in seconds on a GPU rather than hours on a CPU
rsc.tl.leiden(adata, resolution=1.0)

print(adata.obs['leiden'].value_counts())