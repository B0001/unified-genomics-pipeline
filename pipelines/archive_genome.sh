# Final pipeline task: Convert large BAMs to highly compressed CRAMs for deep cold storage
# This utilizes the Rust-based noodles library or standard samtools
samtools view \
    -C \
    -T human_reference_GRCh38.fasta \
    -o patient_archival.cram \
    patient_aligned.bam