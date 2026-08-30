#!/bin/bash
# NGS Pipeline Wrapper - Universal Stage Executor
# Adapts the original pipeline scripts to work within the containerized web wrapper

set -e

STAGE="${1:?Stage name required}"
PROJECT_DIR="${PROJECT_DIR:-.}"
INPUTS_DIR="${INPUTS_DIR:-${PROJECT_DIR}/inputs}"
OUTPUTS_DIR="${OUTPUTS_DIR:-${PROJECT_DIR}/outputs}"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-${PROJECT_DIR}/artifacts}"
LOGS_DIR="${LOGS_DIR:-${PROJECT_DIR}/logs}"

# Source original configuration
if [ -f "/app/scripts/config.sh" ]; then
    source /app/scripts/config.sh
fi

# Override key paths for project isolation
export TRIMMED_READS="${OUTPUTS_DIR}/trimmed"
export SAM_FILES="${OUTPUTS_DIR}/alignment"
export SORTED_BAM="${OUTPUTS_DIR}/sorted"
export VCF_DIR="${OUTPUTS_DIR}/vcf"
export CONSENSUS="${OUTPUTS_DIR}/consensus"
export CHAIN="${OUTPUTS_DIR}/chain"

# Create output directories
mkdir -p "$OUTPUTS_DIR" "$ARTIFACTS_DIR" "$LOGS_DIR"
mkdir -p "$TRIMMED_READS" "$SAM_FILES" "$SORTED_BAM" "$VCF_DIR" "$CONSENSUS" "$CHAIN"

echo "=========================================="
echo "NGS Pipeline - Stage: $STAGE"
echo "=========================================="
echo "Started: $(date)"
echo "Project Directory: $PROJECT_DIR"
echo "Input Directory: $INPUTS_DIR"
echo "Output Directory: $OUTPUTS_DIR"
echo ""

# Execute appropriate stage script
case "$STAGE" in
    getting_data)
        bash /app/scripts/getting_data.sh
        ;;
    fastqc_raw)
        bash /app/scripts/fastqc_trim.sh  # FastQC on raw reads
        ;;
    trimming)
        bash /app/scripts/trimming.sh
        ;;
    fastqc_trim)
        bash /app/scripts/fastqc_trim.sh
        ;;
    multiqc_raw)
        bash /app/scripts/multiqc_raw.sh
        ;;
    multiqc_trim)
        bash /app/scripts/multiqc_trim.sh
        ;;
    reference)
        bash /app/scripts/reference.sh
        ;;
    bwa_alignment)
        bash /app/scripts/bwa_alignment.sh
        ;;
    samtools_sort)
        bash /app/scripts/sorting_sam.sh
        ;;
    variant_calling)
        bash /app/scripts/variant_calling.sh
        ;;
    consensus)
        bash /app/scripts/consensus.sh
        ;;
    cds_extraction)
        python /app/python_scripts/cds_extraction.py
        ;;
    *)
        echo "Unknown stage: $STAGE"
        exit 1
        ;;
esac

# Copy relevant outputs to artifacts
case "$STAGE" in
    multiqc_raw|multiqc_trim)
        if [ -d "$OUTPUTS_DIR/multiqc_report" ]; then
            cp -r "$OUTPUTS_DIR/multiqc_report" "$ARTIFACTS_DIR/" 2>/dev/null || true
        fi
        ;;
    consensus)
        if [ -d "$OUTPUTS_DIR/consensus" ]; then
            cp -r "$OUTPUTS_DIR/consensus" "$ARTIFACTS_DIR/" 2>/dev/null || true
        fi
        ;;
    cds_extraction)
        # Copy extracted CDS files
        find "$OUTPUTS_DIR" -name "*.fasta" -type f -exec cp {} "$ARTIFACTS_DIR/" \; 2>/dev/null || true
        find "$OUTPUTS_DIR" -name "*.fna" -type f -exec cp {} "$ARTIFACTS_DIR/" \; 2>/dev/null || true
        ;;
esac

echo ""
echo "=========================================="
echo "Stage $STAGE completed successfully"
echo "Completed: $(date)"
echo "=========================================="

exit 0
