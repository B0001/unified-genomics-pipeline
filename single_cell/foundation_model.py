from __future__ import annotations
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer
import scanpy as sc

def load_model(model_name: str, device: str = "cuda"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name).to(device)
    return tokenizer, model

def embed_cells(h5ad_path: str, tokenizer, model, device: str = "cuda"):
    adata = sc.read_h5ad(h5ad_path, backed="r")
    inputs = tokenizer(adata.obs["cell_sequences"].tolist(), return_tensors="pt").to(device)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state
    return embeddings
