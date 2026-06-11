# Inside a WDL task or Nextflow process:
# Execute the single statically-linked binary
fastVEP \
    --vcf cohort_variants.vcf \
    --gene-db annotations.oga \
    --interval-db structural_variants.osi \
    --output clinical_annotated.vcf