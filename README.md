# gene — GA4GH Federated Genomics Pipeline Toolkit

A collection of modules for cloud-native, GPU-accelerated genomic analysis
using GA4GH standards (DRS, TES, Passport), Apache Arrow Flight, Crypt4GH,
polars-bio, and RAPIDS SingleCell.

---

## Directory layout

```
gene/
├── auth/                    # GA4GH Passport authentication
│   ├── ga4gh_passport.py    # (was authenticate_ga4gh_passport.py)
│   └── federated.py         # (was federated_auth.py)
│
├── drs/                     # Data Repository Service resolution
│   └── resolution.py        # (was drs_resolution.py)
│
├── variants/                # Variant analysis
│   ├── annotation.py        # VEP annotation   (was annotate_variants.py)
│   └── analysis.py          # Overlap/nearest  (was variant_analysis.py)
│
├── single_cell/             # Single-cell RNA analysis
│   ├── gpu_analysis.py      # RAPIDS pipeline  (was gpu_single_cell_analysis.py)
│   ├── dask_orchestration.py# Multi-GPU Dask   (was dask_gpu_orchestration.py)
│   └── foundation_model.py  # Transformer infer(was foundation_model_inference.py)
│
├── storage/                 # Data storage & encryption
│   ├── encryption.py        # Crypt4GH         (was crypt4gh_encryption.py)
│   └── cloud_access.py      # OpenDAL/cloud IO (was composable_data_access.py)
│
├── server/                  # Data serving
│   └── flight_server.py     # Arrow Flight gRPC(was genomic_flight_server.py)
│
├── visualization/           # Frontend & Rust visualizations
│   ├── clinical_drs_dashboard.jsx   (was clinical_drs_dashboard.jsx — improved)
│   └── clinical_visualization.rs   (Rust, unchanged)
│
├── pipelines/               # Workflow definitions & runner scripts
│   ├── variant_calling.wdl          (was variant_calling.wdl)
│   ├── embarrassingly_fasta.nf      (was embarrassingly_fasta.nf)
│   ├── archive_genome.sh            (was archive_genome.sh)
│   ├── run_fastvep.sh               (was run_fastvep.sh)
│   ├── run_giraffe_alignment.sh     (was run_giraffe_alignment.sh)
│   └── run_gwas.sh                  (was run_gwas.sh)
│
├── rust/                    # Rust workspace
│   ├── Cargo.toml
│   └── src/
│       ├── bam_reader.rs            (was read_bam.rs)
│       └── clinical_viz.rs          (was clinical_visualization.rs)
│
├── infra/                   # Kubernetes / TESK templates
│   └── tesk_job_template.yaml       (unchanged)
│
└── tests/
    ├── conftest.py          # Shared fixtures + external-dep stubs
    ├── unit/
    │   ├── test_auth.py
    │   ├── test_drs.py
    │   ├── test_variants.py
    │   ├── test_storage.py
    │   ├── test_server.py
    │   ├── test_single_cell.py
    │   └── test_pipelines.py   # script/YAML/WDL structural checks
    └── integration/
        └── test_drs_integration.py  # (was test_drs_connection.py)
```

---

## Running tests

```bash
# Install dev deps
pip install -e ".[dev]"

# Unit tests only (no GPU, no cloud, no live DRS needed)
pytest

# With coverage report
pytest --cov --cov-report=term-missing

# Include integration tests (requires a live DRS endpoint)
pytest -m integration --drs-url http://localhost:9101/ga4gh/drs/v1/ --jwt YOUR_TOKEN
```

---

## Key design choices

| Choice | Rationale |
|--------|-----------|
| All heavy deps stubbed in `conftest.py` | Tests run in any CI environment — no GPU or specialised bioinformatics packages required |
| Source files refactored into named functions | Plain scripts cannot be unit-tested; functions can |
| `set -euo pipefail` enforced on all shell scripts | Prevents silent failures in long-running pipeline steps |
| Integration tests skipped by default | Keeps `pytest` green without a running DRS node; opt-in with `-m integration` |
| 80 % coverage threshold in `pyproject.toml` | Enforced by `pytest-cov`; fails the build if coverage drops |
