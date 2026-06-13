from __future__ import annotations
import polars_bio as pb

def read_cloud_variants(vcf_uri: str):
    return pb.read_vcf(vcf_uri)

def read_cloud_genes(bed_uri: str):
    return pb.read_bed(bed_uri)

def overlap_cloud_data(vcf_uri: str, bed_uri: str):
    return pb.overlap(read_cloud_variants(vcf_uri), read_cloud_genes(bed_uri))
