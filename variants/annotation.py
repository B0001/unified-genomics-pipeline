from __future__ import annotations
import polars as pl
import polars_bio as pb

def annotate_variants(vcf_path: str):
    df_variants = pb.read_vcf(vcf_path)
    return df_variants.with_columns(
        pb.expr.vep_consequence(
            chromosome=pl.col("contig"),
            position=pl.col("pos_start"),
            allele=pl.col("alt_allele"),
        ).alias("clinical_consequence")
    )
