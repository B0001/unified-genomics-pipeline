import polars as pl
import polars_bio as pb
# Assuming 'vepyr' functions are registered in the DataFusion context

# Load the zero-copy variant DataFrame
df_variants = pb.read_vcf("cohort_variants.vcf")

# Execute a highly parallelized variant effect prediction natively in memory
# This bypasses the need to write intermediate VCFs to disk
annotated_variants = df_variants.with_columns(
    pb.expr.vep_consequence(
        chromosome=pl.col("contig"),
        position=pl.col("pos_start"),
        allele=pl.col("alt_allele")
    ).alias("clinical_consequence")
)