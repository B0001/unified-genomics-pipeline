from __future__ import annotations
import polars_bio as pb

def load_variants_and_genes(vcf_path: str, bed_path: str):
    return pb.read_vcf(vcf_path), pb.read_bed(bed_path)

def find_overlapping_variants(df_variants, df_genes):
    return pb.overlap(df_variants, df_genes)

def find_nearest_genes(df_variants, df_genes):
    return pb.nearest(df_variants, df_genes)
