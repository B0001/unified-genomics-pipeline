version 1.0

workflow UnifiedVariantCalling {
    input {
        File raw_fastq_1
        File raw_fastq_2
        File reference_genome
    }

    # Orchestration layer dynamically provisions the required cloud instances
    call ParabricksGPU {
        input:
            fq1 = raw_fastq_1,
            fq2 = raw_fastq_2,
            ref = reference_genome
    }
}

task ParabricksGPU {
    input {
        File fq1
        File fq2
        File ref
    }
    command <<<
        # Utilizing TensorRT and CUDA-optimized compute kernels
        pbrun germline \
        --ref ~{ref} \
        --in-fq ~{fq1} ~{fq2} \
        --out-variants variants.vcf \
        --out-bam aligned.bam
    >>>
    runtime {
        # Running inside the unified NVIDIA NGC container
        docker: "nvcr.io/nvidia/clara/clara-parabricks:4.4.0"
        gpu: true
        memory: "64 GB"
    }
}