"""Regression tests for pipeline scripts and infrastructure files.

These tests validate structure and correctness without executing the
actual bioinformatics tools (which require GPU hardware and large data).
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml  # stdlib-safe; falls back gracefully if PyYAML is missing

PIPELINES = Path(__file__).parents[2] / "pipelines"
INFRA = Path(__file__).parents[2] / "infra"


# ---------------------------------------------------------------------------
# Shell scripts: syntax and key-argument checks
# ---------------------------------------------------------------------------

def bash_syntax_ok(path: Path) -> bool:
    """Return True if bash -n reports no syntax errors."""
    result = subprocess.run(
        ["bash", "-n", str(path)], capture_output=True
    )
    return result.returncode == 0


class TestShellScripts:
    SCRIPTS = [
        "archive_genome.sh",
        "run_fastvep.sh",
        "run_giraffe_alignment.sh",
        "run_gwas.sh",
    ]

    @pytest.mark.parametrize("script_name", SCRIPTS)
    def test_script_exists(self, script_name):
        assert (PIPELINES / script_name).is_file(), f"{script_name} not found"

    @pytest.mark.parametrize("script_name", SCRIPTS)
    def test_script_is_executable(self, script_name):
        path = PIPELINES / script_name
        assert os.access(path, os.X_OK), f"{script_name} is not executable"

    @pytest.mark.parametrize("script_name", SCRIPTS)
    def test_bash_syntax_is_valid(self, script_name):
        path = PIPELINES / script_name
        assert bash_syntax_ok(path), f"{script_name} has bash syntax errors"

    @pytest.mark.parametrize("script_name", SCRIPTS)
    def test_set_e_is_present(self, script_name):
        """All scripts must use set -euo pipefail for safety."""
        content = (PIPELINES / script_name).read_text()
        assert "set -euo pipefail" in content, (
            f"{script_name} missing 'set -euo pipefail'"
        )

    def test_archive_genome_uses_samtools_view(self):
        content = (PIPELINES / "archive_genome.sh").read_text()
        assert "samtools view" in content

    def test_archive_genome_produces_cram(self):
        content = (PIPELINES / "archive_genome.sh").read_text()
        assert ".cram" in content

    def test_run_fastvep_specifies_vcf_flag(self):
        content = (PIPELINES / "run_fastvep.sh").read_text()
        assert "--vcf" in content

    def test_run_fastvep_specifies_output_flag(self):
        content = (PIPELINES / "run_fastvep.sh").read_text()
        assert "--output" in content

    def test_run_giraffe_specifies_pangenome_ref(self):
        content = (PIPELINES / "run_giraffe_alignment.sh").read_text()
        assert "--ref-gbz" in content

    def test_run_giraffe_produces_bam(self):
        content = (PIPELINES / "run_giraffe_alignment.sh").read_text()
        assert "--out-bam" in content

    def test_run_gwas_uses_gpu_flag(self):
        content = (PIPELINES / "run_gwas.sh").read_text()
        assert "--use-gpu" in content

    def test_run_gwas_specifies_phenotype_file(self):
        content = (PIPELINES / "run_gwas.sh").read_text()
        assert "--pheno" in content


# ---------------------------------------------------------------------------
# WDL workflow: structural validation
# ---------------------------------------------------------------------------

class TestVariantCallingWdl:
    WDL_PATH = PIPELINES / "variant_calling.wdl"

    def test_wdl_file_exists(self):
        assert self.WDL_PATH.is_file()

    def test_declares_version_1(self):
        content = self.WDL_PATH.read_text()
        assert "version 1.0" in content

    def test_defines_unified_variant_calling_workflow(self):
        content = self.WDL_PATH.read_text()
        assert "workflow UnifiedVariantCalling" in content

    def test_defines_parabricks_gpu_task(self):
        content = self.WDL_PATH.read_text()
        assert "task ParabricksGPU" in content

    def test_runtime_specifies_gpu(self):
        content = self.WDL_PATH.read_text()
        assert "gpu: true" in content

    def test_runtime_specifies_parabricks_docker_image(self):
        content = self.WDL_PATH.read_text()
        assert "clara-parabricks" in content

    def test_workflow_inputs_include_fastq_pair(self):
        content = self.WDL_PATH.read_text()
        assert "raw_fastq_1" in content
        assert "raw_fastq_2" in content

    def test_pbrun_germline_command_present(self):
        content = self.WDL_PATH.read_text()
        assert "pbrun germline" in content


# ---------------------------------------------------------------------------
# Nextflow pipeline: key directives
# ---------------------------------------------------------------------------

class TestEmbarrassinglyFastaNf:
    NF_PATH = PIPELINES / "embarrassingly_fasta.nf"

    def test_nextflow_file_exists(self):
        assert self.NF_PATH.is_file()

    def test_references_parabricks_germline(self):
        content = self.NF_PATH.read_text()
        assert "pbrun germline" in content

    def test_references_fastvep(self):
        content = self.NF_PATH.read_text()
        assert "fastVEP" in content

    def test_removes_intermediate_bam(self):
        """Intermediate BAM must be deleted to prevent storage cost inflation."""
        content = self.NF_PATH.read_text()
        assert "rm intermediate.bam" in content

    def test_produces_cram_output(self):
        content = self.NF_PATH.read_text()
        assert "samtools view" in content


# ---------------------------------------------------------------------------
# TESK Kubernetes job template: schema validation
# ---------------------------------------------------------------------------

class TestTeskJobTemplate:
    YAML_PATH = INFRA / "tesk_job_template.yaml"

    def test_yaml_file_exists(self):
        assert self.YAML_PATH.is_file()

    def test_yaml_parses_without_error(self):
        content = self.YAML_PATH.read_text()
        doc = yaml.safe_load(content)
        assert doc is not None

    def test_api_version_is_batch_v1(self):
        doc = yaml.safe_load(self.YAML_PATH.read_text())
        assert doc["apiVersion"] == "batch/v1"

    def test_kind_is_job(self):
        doc = yaml.safe_load(self.YAML_PATH.read_text())
        assert doc["kind"] == "Job"

    def test_restart_policy_is_never(self):
        doc = yaml.safe_load(self.YAML_PATH.read_text())
        policy = doc["spec"]["template"]["spec"]["restartPolicy"]
        assert policy == "Never"

    def test_container_has_memory_limit(self):
        doc = yaml.safe_load(self.YAML_PATH.read_text())
        containers = doc["spec"]["template"]["spec"]["containers"]
        assert len(containers) > 0
        limits = containers[0]["resources"]["limits"]
        assert "memory" in limits

    def test_container_has_cpu_limit(self):
        doc = yaml.safe_load(self.YAML_PATH.read_text())
        containers = doc["spec"]["template"]["spec"]["containers"]
        limits = containers[0]["resources"]["limits"]
        assert "cpu" in limits

    def test_fastvep_image_is_specified(self):
        doc = yaml.safe_load(self.YAML_PATH.read_text())
        containers = doc["spec"]["template"]["spec"]["containers"]
        images = [c["image"] for c in containers]
        assert any("fastvep" in img for img in images)
