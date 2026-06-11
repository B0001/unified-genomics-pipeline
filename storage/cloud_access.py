import polars_bio as pb

# polars-bio natively uses Apache OpenDAL to stream data directly from cloud storage
# This completely decouples the compute engine from the storage backend.
df_variants = pb.read_vcf("s3://global-biobank-bucket/cohort_data.vcf.gz")
df_genes = pb.read_bed("gcs://reference-bucket/target_genes.bed")

# Execute the overlap query in-memory using Apache Arrow and DataFusion
overlapping = pb.overlap(df_variants, df_genes)
print(overlapping.head())