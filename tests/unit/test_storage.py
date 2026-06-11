"""Regression tests for storage.encryption and storage.cloud_access."""
from __future__ import annotations

from unittest.mock import MagicMock, call, mock_open, patch

import pytest

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))

import crypt4gh.keys as c4gh_keys
import crypt4gh.lib as c4gh_lib
import polars_bio as pb

from storage.encryption import decrypt_file, encrypt_file, load_keys
from storage.cloud_access import overlap_cloud_data, read_cloud_genes, read_cloud_variants


# ---------------------------------------------------------------------------
# load_keys
# ---------------------------------------------------------------------------

class TestLoadKeys:
    def test_returns_list_with_one_triple(self):
        c4gh_keys.get_private_key.return_value = b"privk"
        c4gh_keys.get_public_key.return_value = b"pubk"
        keys = load_keys("node.sec", "node.pub", "password")
        assert isinstance(keys, list)
        assert len(keys) == 1
        mode, priv, pub = keys[0]
        assert mode == 0
        assert priv == b"privk"
        assert pub == b"pubk"

    def test_passes_correct_paths_to_key_loaders(self):
        load_keys("my.sec", "my.pub", "secret")
        c4gh_keys.get_private_key.assert_called_with("my.sec", callback=pytest.approx)
        c4gh_keys.get_public_key.assert_called_with("my.pub")

    def test_password_is_forwarded_via_callback(self):
        """The callback passed to get_private_key must return the password."""
        captured = {}

        def fake_get_private_key(path, callback):
            captured["result"] = callback()
            return b"privk"

        c4gh_keys.get_private_key.side_effect = fake_get_private_key
        load_keys("a.sec", "a.pub", "mysecretpassword")
        assert captured["result"] == "mysecretpassword"
        c4gh_keys.get_private_key.side_effect = None  # reset

    def test_empty_password_is_accepted(self):
        c4gh_keys.get_private_key.return_value = b"privk"
        c4gh_keys.get_public_key.return_value = b"pubk"
        keys = load_keys("a.sec", "a.pub")  # default password=""
        assert len(keys) == 1


# ---------------------------------------------------------------------------
# encrypt_file
# ---------------------------------------------------------------------------

class TestEncryptFile:
    def test_calls_crypt4gh_encrypt(self, tmp_plaintext_file, tmp_encrypted_path):
        keys = [(0, b"priv", b"pub")]
        c4gh_lib.encrypt.reset_mock()
        encrypt_file(keys, tmp_plaintext_file, tmp_encrypted_path)
        c4gh_lib.encrypt.assert_called_once()

    def test_passes_keys_as_first_argument(self, tmp_plaintext_file, tmp_encrypted_path):
        keys = [(0, b"priv", b"pub")]
        c4gh_lib.encrypt.reset_mock()
        encrypt_file(keys, tmp_plaintext_file, tmp_encrypted_path)
        called_keys = c4gh_lib.encrypt.call_args.args[0]
        assert called_keys is keys

    def test_opens_input_file_in_binary_read_mode(self, tmp_plaintext_file, tmp_encrypted_path):
        """Ensure we open files correctly — binary read for input."""
        keys = [(0, b"priv", b"pub")]
        opened_modes: list[str] = []
        real_open = open

        def tracking_open(path, mode="r", **kwargs):
            opened_modes.append(mode)
            return real_open(path, mode, **kwargs)

        with patch("builtins.open", side_effect=tracking_open):
            encrypt_file(keys, tmp_plaintext_file, tmp_encrypted_path)

        assert "rb" in opened_modes
        assert "wb" in opened_modes

    def test_raises_file_not_found_for_missing_input(self, tmp_encrypted_path):
        keys = [(0, b"priv", b"pub")]
        with pytest.raises(FileNotFoundError):
            encrypt_file(keys, "/nonexistent/input.fastq", tmp_encrypted_path)


# ---------------------------------------------------------------------------
# decrypt_file
# ---------------------------------------------------------------------------

class TestDecryptFile:
    def test_calls_crypt4gh_decrypt(self, tmp_plaintext_file, tmp_decrypted_path):
        keys = [(0, b"priv", b"pub")]
        c4gh_lib.decrypt.reset_mock()
        decrypt_file(keys, tmp_plaintext_file, tmp_decrypted_path)
        c4gh_lib.decrypt.assert_called_once()

    def test_passes_keys_as_first_argument(self, tmp_plaintext_file, tmp_decrypted_path):
        keys = [(0, b"priv", b"pub")]
        decrypt_file(keys, tmp_plaintext_file, tmp_decrypted_path)
        called_keys = c4gh_lib.decrypt.call_args.args[0]
        assert called_keys is keys


# ---------------------------------------------------------------------------
# read_cloud_variants
# ---------------------------------------------------------------------------

class TestReadCloudVariants:
    def test_delegates_to_pb_read_vcf(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        result = read_cloud_variants("s3://bucket/cohort.vcf.gz")
        pb.read_vcf.assert_called_with("s3://bucket/cohort.vcf.gz")
        assert result is mock_polars_df

    @pytest.mark.parametrize("uri", [
        "s3://bucket/a.vcf",
        "gs://ref/b.vcf.gz",
        "az://store/c.vcf",
    ])
    def test_accepts_all_cloud_uri_schemes(self, uri, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        read_cloud_variants(uri)
        pb.read_vcf.assert_called_with(uri)


# ---------------------------------------------------------------------------
# read_cloud_genes
# ---------------------------------------------------------------------------

class TestReadCloudGenes:
    def test_delegates_to_pb_read_bed(self, mock_polars_df):
        pb.read_bed.return_value = mock_polars_df
        result = read_cloud_genes("gcs://reference/genes.bed")
        pb.read_bed.assert_called_with("gcs://reference/genes.bed")
        assert result is mock_polars_df


# ---------------------------------------------------------------------------
# overlap_cloud_data
# ---------------------------------------------------------------------------

class TestOverlapCloudData:
    def test_returns_overlap_result(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        pb.read_bed.return_value = mock_polars_df
        pb.overlap.return_value = mock_polars_df

        result = overlap_cloud_data("s3://v.vcf.gz", "gcs://g.bed")
        pb.overlap.assert_called_once_with(mock_polars_df, mock_polars_df)
        assert result is mock_polars_df

    def test_reads_both_sources_before_overlap(self, mock_polars_df):
        pb.read_vcf.return_value = mock_polars_df
        pb.read_bed.return_value = mock_polars_df
        pb.overlap.return_value = mock_polars_df
        pb.read_vcf.reset_mock()
        pb.read_bed.reset_mock()

        overlap_cloud_data("s3://v.vcf.gz", "gcs://g.bed")
        assert pb.read_vcf.call_count == 1
        assert pb.read_bed.call_count == 1
