"""Regression tests for variants.annotation and variants.analysis."""
from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))

import polars_bio as pb  # the stub registered in conftest
from variants.annotation import annotate_variants
from variants.analysis import (
    find_nearest_genes,
    find_overlapping_variants,
    load_variants_and_genes,
)


# ---------------------------------------------------------------------------
# annotate_variants
# ---------------------------------------------------------------------------

class TestAnnotateVariants:
    def test_reads_vcf_from_given_path(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        annotate_variants("cohort.vcf")
        pb.read_vcf.assert_called_with("cohort.vcf")

    def test_adds_clinical_consequence_column(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        result = annotate_variants("cohort.vcf")
        # with_columns must have been called on the DataFrame
        mock_polars_df.with_columns.assert_called_once()
        assert result is mock_polars_df.with_columns.return_value

    def test_uses_vep_consequence_expression(self, mock_polars_df):
        """Verify that pb.expr.vep_consequence is invoked (not a hard-coded value)."""
        pb.read_vcf.return_value = mock_polars_df
        annotate_variants("cohort.vcf")
        pb.expr.vep_consequence.assert_called()

    def test_accepts_cloud_uri_as_path(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        annotate_variants("s3://biobank/variants.vcf.gz")
        pb.read_vcf.assert_called_with("s3://biobank/variants.vcf.gz")

    def test_propagates_read_error(self):
        pb.read_vcf.side_effect = FileNotFoundError("VCF not found")
        with pytest.raises(FileNotFoundError):
            annotate_variants("missing.vcf")
        pb.read_vcf.side_effect = None  # reset for subsequent tests


# ---------------------------------------------------------------------------
# load_variants_and_genes
# ---------------------------------------------------------------------------

class TestLoadVariantsAndGenes:
    def test_returns_tuple_of_two_dataframes(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        pb.read_bed.return_value = mock_polars_df

        variants, genes = load_variants_and_genes("v.vcf", "g.bed")
        assert variants is mock_polars_df
        assert genes is mock_polars_df

    def test_reads_vcf_and_bed_with_correct_paths(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        pb.read_bed.return_value = mock_polars_df

        load_variants_and_genes("path/to/cohort.vcf", "path/to/genes.bed")
        pb.read_vcf.assert_called_with("path/to/cohort.vcf")
        pb.read_bed.assert_called_with("path/to/genes.bed")

    def test_accepts_cloud_uris(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        pb.read_bed.return_value = mock_polars_df

        load_variants_and_genes(
            "s3://global-biobank/cohort.vcf.gz",
            "gcs://reference/genes.bed",
        )
        pb.read_vcf.assert_called_with("s3://global-biobank/cohort.vcf.gz")
        pb.read_bed.assert_called_with("gcs://reference/genes.bed")


# ---------------------------------------------------------------------------
# find_overlapping_variants
# ---------------------------------------------------------------------------

class TestFindOverlappingVariants:
    def test_delegates_to_pb_overlap(self, mock_polars_df):
        pb.overlap.return_value = mock_polars_df
        df_v, df_g = MagicMock(), MagicMock()
        result = find_overlapping_variants(df_v, df_g)
        pb.overlap.assert_called_once_with(df_v, df_g)
        assert result is mock_polars_df

    def test_passes_correct_argument_order(self, mock_polars_df):
        pb.overlap.return_value = mock_polars_df
        df_v, df_g = MagicMock(name="variants"), MagicMock(name="genes")
        find_overlapping_variants(df_v, df_g)
        args = pb.overlap.call_args.args
        assert args[0] is df_v
        assert args[1] is df_g


# ---------------------------------------------------------------------------
# find_nearest_genes
# ---------------------------------------------------------------------------

class TestFindNearestGenes:
    def test_delegates_to_pb_nearest(self, mock_polars_df):
        pb.nearest.return_value = mock_polars_df
        df_v, df_g = MagicMock(), MagicMock()
        result = find_nearest_genes(df_v, df_g)
        pb.nearest.assert_called_once_with(df_v, df_g)
        assert result is mock_polars_df

    def test_passes_variants_before_genes(self, mock_polars_df):
        pb.nearest.return_value = mock_polars_df
        df_v, df_g = MagicMock(name="variants"), MagicMock(name="genes")
        find_nearest_genes(df_v, df_g)
        args = pb.nearest.call_args.args
        assert args[0] is df_v
        assert args[1] is df_g
