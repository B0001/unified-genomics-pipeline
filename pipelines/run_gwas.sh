# Execute the GPU-accelerated mixed-model association tool directly 
# on the UK Biobank Research Analysis Platform
quickdraws \
    --bfile ukb_imputed_data \
    --pheno ukb_phenotypes.txt \
    --trait-type binary \
    --prior spike-and-slab \
    --out ukb_results \
    --use-gpu