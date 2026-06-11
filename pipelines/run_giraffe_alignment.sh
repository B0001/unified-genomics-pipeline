# Utilizing NVIDIA Parabricks Giraffe to align short reads 
# against the compressed pangenome graph instead of a linear reference
pbrun giraffe \
    --ref-gbz human_pangenome_1000G.gbz \
    --in-fq1 patient_reads_R1.fastq.gz \
    --in-fq2 patient_reads_R2.fastq.gz \
    --out-bam pangenome_aligned.bam