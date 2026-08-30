#!/bin/bash
# Quick Start Script for NGS Pipeline Web Wrapper
# This script sets up the environment and starts the container

set -e

echo "=================================================="
echo "NGS Pipeline Web Wrapper - Quick Start"
echo "=================================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo ""
echo "✓ Docker and Docker Compose found"
echo ""

# Get repository root
REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$REPO_ROOT"

echo "Repository root: $REPO_ROOT"
echo ""

# Create required directories
echo "Creating data directories..."
mkdir -p data/input_queue
mkdir -p data/projects
mkdir -p data/raw_reads
mkdir -p data/reference
mkdir -p logs

echo "✓ Data directories created"
echo ""

# Check if reference genome exists
if [ ! -f "data/reference/tb_ref_genome/ncbi_dataset/data/GCF_000195955.2/GCF_000195955.2_ASM19595v2_genomic.fna" ]; then
    echo "WARNING: Reference genome not found at expected path"
    echo "The pipeline will attempt to download it if SRA Toolkit is available"
    echo ""
    echo "If you have a reference genome, please place it at:"
    echo "  data/reference/tb_ref_genome/ncbi_dataset/data/GCF_000195955.2/GCF_000195955.2_ASM19595v2_genomic.fna"
    echo ""
fi

# Create sample input files
echo "Creating sample input files..."
cat > data/input_queue/sample_accessions.txt << 'EOF'
# Example SRA Accession IDs for testing
# Uncomment and modify with your actual SRA IDs
# SRR1234567
# SRR1234568
EOF

echo "✓ Sample input file created at: data/input_queue/sample_accessions.txt"
echo ""

# Check available memory
if command -v free &> /dev/null; then
    MEMORY=$(free -g | awk 'NR==2 {print $2}')
    if [ "$MEMORY" -lt 4 ]; then
        echo "WARNING: Only ${MEMORY}GB RAM available. Recommended: at least 4GB"
        echo ""
    fi
fi

# Display options
echo "=================================================="
echo "Available commands:"
echo "=================================================="
echo ""
echo "1. Build and start container (recommended):"
echo "   docker-compose up -d"
echo ""
echo "2. View container logs:"
echo "   docker-compose logs -f ngs-pipeline-web"
echo ""
echo "3. Stop container:"
echo "   docker-compose down"
echo ""
echo "4. Access web interface:"
echo "   - Open http://localhost:7860 in your browser"
echo "   - API Documentation: http://localhost:7860/docs"
echo "   - Health Check: http://localhost:7860/api/health"
echo ""
echo "5. Place sample files:"
echo "   - Copy FASTQ files to: data/input_queue/"
echo "   - Or SRA accession IDs to: data/input_queue/*.txt"
echo ""
echo "6. Create a project via API:"
echo "   curl -X POST http://localhost:7860/api/projects/create"
echo ""
echo "=================================================="
echo ""
echo "Ready to start! Run: docker-compose up -d"
echo ""
