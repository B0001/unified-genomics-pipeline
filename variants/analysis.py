import polars as pl
import polars_bio as pb

# Read variant and gene boundary data natively into Arrow-backed DataFrames
# The coordinate system defaults to 1-based closed coordinates
df_variants = pb.read_vcf("cohort_variants.vcf")
df_genes = pb.read_bed("target_genes.bed")

# Execute an out-of-core overlap query across millions of intervals
overlapping_variants = pb.overlap(df_variants, df_genes)

# You can also run nearest neighbor distance queries just as efficiently
nearest_genes = pb.nearest(df_variants, df_genes)

print(overlapping_variants.head())