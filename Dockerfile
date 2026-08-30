# NGS Pipeline Web Wrapper - Production Dockerfile
# Based on ubuntu:24.04
# Includes conda environment with all bioinformatics tools and Python web server

FROM ubuntu:24.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/miniconda3/bin:$PATH \
    PORT=7860

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN curl -sL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/miniconda3 && \
    rm /tmp/miniconda.sh && \
    conda clean --all -y

# Create main conda environment with all bioinformatics tools
# Using a comprehensive single environment to avoid dependency conflicts
RUN conda config --add channels conda-forge && \
    conda config --add channels bioconda && \
    conda create -n ngs_env -y -c conda-forge -c bioconda \
    sra-tools \
    fastqc \
    multiqc \
    trimmomatic \
    bwa \
    samtools \
    bcftools \
    biopython \
    python=3.11 \
    pip \
    && conda clean --all -y

# Activate environment and install pip packages
SHELL ["conda", "run", "-n", "ngs_env", "/bin/bash", "-c"]

# Install Python web server dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    watchdog==3.0.0 \
    jinja2==3.1.2 \
    python-multipart==0.0.6 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    pyliftover==0.4

# Create application directory structure
RUN mkdir -p /app/data/input_queue /app/data/projects /app/scripts /app/webapp

# Set working directory
WORKDIR /app

# Copy application code
COPY webapp/ /app/webapp/

# Expose port
EXPOSE ${PORT}

# Default port environment variable
ENV PORT=7860

# Create initialization script
RUN mkdir -p /app/entrypoint && \
    echo '#!/bin/bash\n\
source /opt/miniconda3/etc/profile.d/conda.sh\n\
conda activate ngs_env\n\
\n\
# Ensure data directories exist\n\
mkdir -p /app/data/input_queue\n\
mkdir -p /app/data/projects\n\
\n\
# Start the FastAPI application\n\
cd /app/webapp\n\
python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --reload\n\
' > /app/entrypoint/start.sh && \
    chmod +x /app/entrypoint/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Run the application
ENTRYPOINT ["/app/entrypoint/start.sh"]
