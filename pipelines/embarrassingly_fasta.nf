process EmbarrassinglyFASTA_GPU {
    // Trigger ephemeral cloud pricing (Spot Instances) to drop compute costs
    machineType 'gpu-spot-instance' 

    input:
    tuple val(sample_id), path(reads)

    output:
    path "${sample_id}_annotated.vcf"
    path "${sample_id}_final.cram"

    script:
    """
    # 1. Align reads and call variants directly into a VCF using Parabricks
    pbrun germline \
        --ref reference.fasta \
        --in-fq ${reads} ${reads[1]} \
        --out-variants ${sample_id}_raw.vcf \
        --out-bam intermediate.bam

    # 2. Immediately run rapid clinical annotation via fastVEP
    fastVEP \
        --vcf ${sample_id}_raw.vcf \
        --gene-db annotations.oga \
        --output ${sample_id}_annotated.vcf

    # 3. Compress the intermediate file into a highly efficient CRAM for deep storage
    samtools view -C -T reference.fasta -o ${sample_id}_final.cram intermediate.bam

    # 4. Destroy the massive intermediate BAM file before the cloud instance terminates
    # This completely prevents the data from ever egressing or inflating storage costs
    rm intermediate.bam
    """
}