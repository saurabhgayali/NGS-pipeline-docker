"""
NGS Pipeline Web Wrapper - Configuration
Central configuration for the web application
"""

import os
from pathlib import Path
from typing import Dict, List

# ============================================================================
# DIRECTORY CONFIGURATION
# ============================================================================

# Base directory for all data
BASE_DATA_DIR = Path(os.getenv("BASE_DATA_DIR", "/app/data"))

# Input queue directory - files placed here trigger project creation
INPUT_QUEUE_DIR = BASE_DATA_DIR / "input_queue"

# Projects directory - all projects stored here
PROJECTS_DIR = BASE_DATA_DIR / "projects"

# Scripts directory - pipeline scripts
SCRIPTS_DIR = Path(os.getenv("SCRIPTS_DIR", "/app/scripts"))

# Python scripts directory
PYTHON_SCRIPTS_DIR = Path(os.getenv("PYTHON_SCRIPTS_DIR", "/app/python_scripts"))

# ============================================================================
# WEB SERVER CONFIGURATION
# ============================================================================

# Web server port
PORT = int(os.getenv("PORT", 7860))

# Web server host
HOST = os.getenv("HOST", "0.0.0.0")

# Enable debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Log level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# PIPELINE CONFIGURATION
# ============================================================================

# Pipeline stages in execution order
PIPELINE_STAGES: List[str] = [
    "getting_data",        # SRA download & FASTQ conversion
    "fastqc_raw",          # Raw read quality control
    "trimming",            # Adapter & quality trimming
    "fastqc_trim",         # Trimmed read quality control
    "multiqc_raw",         # Aggregate raw QC report
    "multiqc_trim",        # Aggregate trimmed QC report
    "reference",           # Reference genome indexing
    "bwa_alignment",       # Read alignment to reference
    "samtools_sort",       # SAM to BAM conversion & sorting
    "variant_calling",     # Variant calling
    "consensus",           # Consensus sequence generation
    "cds_extraction"       # CDS extraction from consensus
]

# Stage dependencies (optional - for future parallel execution)
STAGE_DEPENDENCIES: Dict[str, List[str]] = {
    "fastqc_raw": ["getting_data"],
    "trimming": ["fastqc_raw"],
    "fastqc_trim": ["trimming"],
    "multiqc_raw": ["fastqc_raw"],
    "multiqc_trim": ["fastqc_trim"],
    "reference": [],  # Can run anytime
    "bwa_alignment": ["reference", "trimming"],
    "samtools_sort": ["bwa_alignment"],
    "variant_calling": ["samtools_sort"],
    "consensus": ["variant_calling"],
    "cds_extraction": ["consensus"]
}

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

# Project metadata filename
PROJECT_METADATA_FILE = "metadata.json"

# Dashboard filename
DASHBOARD_FILE = "index.html"

# Project subdirectories
PROJECT_SUBDIRS = [
    "inputs",          # Input FASTQ/SRA files
    "outputs",         # Pipeline intermediate & final outputs
    "logs",            # Per-stage log files
    "artifacts"        # Final deliverables
]

# ============================================================================
# FILE MONITORING CONFIGURATION
# ============================================================================

# File extensions to monitor
MONITORED_EXTENSIONS = {
    '.fastq', '.fq',           # FASTQ formats
    '.fastq.gz', '.fq.gz',     # Compressed FASTQ
    '.sra',                    # SRA format
    '.txt', '.csv',            # Accession ID lists
    '.gz'                      # Generic compressed
}

# Minimum file size to consider (bytes, helps avoid partial files)
MIN_FILE_SIZE = 1024  # 1 KB

# Settle time before processing (seconds, wait for file write to complete)
FILE_SETTLE_TIME = 2

# ============================================================================
# EXECUTION CONFIGURATION
# ============================================================================

# Environment variables passed to pipeline scripts
PIPELINE_ENV_VARS = {
    "PYTHONUNBUFFERED": "1",
    "CONDA_DEFAULT_ENV": "ngs_env"
}

# Command timeout for pipeline stages (seconds)
STAGE_TIMEOUT = 86400  # 24 hours

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

# Maximum upload file size (bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB

# CORS allowed origins
CORS_ORIGINS = ["*"]

# Enable CORS credentials
CORS_CREDENTIALS = True

# CORS allowed methods
CORS_METHODS = ["*"]

# CORS allowed headers
CORS_HEADERS = ["*"]

# ============================================================================
# DASHBOARD CONFIGURATION
# ============================================================================

# Dashboard refresh interval (seconds)
DASHBOARD_REFRESH_INTERVAL = 5

# Number of log lines to show in modal
LOG_LINES_LIMIT = 500

# Number of recent logs to include in status
RECENT_LOG_LINES = 20

# ============================================================================
# ARTIFACT CONFIGURATION
# ============================================================================

# File types to automatically collect as artifacts
ARTIFACT_EXTENSIONS = {
    # Quality control
    '.html', '.json',
    # FASTA/FastQ
    '.fasta', '.fa', '.fna', '.faa', '.fastq', '.fq',
    # Compressed
    '.gz', '.tar', '.tar.gz',
    # Text reports
    '.txt', '.csv', '.tsv',
    # Specialized formats
    '.vcf', '.bam', '.sam'
}

# Maximum artifacts to list (prevents huge directory listings)
MAX_ARTIFACTS_LIST = 1000

# ============================================================================
# CONDA CONFIGURATION
# ============================================================================

# Conda environment name
CONDA_ENV = "ngs_env"

# Conda initialization script
CONDA_INIT_SCRIPT = "/opt/miniconda3/etc/profile.d/conda.sh"

# ============================================================================
# NOTIFICATION CONFIGURATION (for future enhancement)
# ============================================================================

# Enable email notifications
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

# Email settings
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "localhost"),
    "smtp_port": int(os.getenv("SMTP_PORT", 25)),
    "from_address": os.getenv("FROM_ADDRESS", "ngs-pipeline@localhost"),
    "to_addresses": os.getenv("TO_ADDRESSES", "").split(",") if os.getenv("TO_ADDRESSES") else []
}

# Enable Slack notifications
SLACK_ENABLED = os.getenv("SLACK_ENABLED", "false").lower() == "true"

# Slack settings
SLACK_CONFIG = {
    "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
    "channel": os.getenv("SLACK_CHANNEL", "#pipeline-notifications")
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        BASE_DATA_DIR,
        INPUT_QUEUE_DIR,
        PROJECTS_DIR,
        SCRIPTS_DIR,
        PYTHON_SCRIPTS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(directory, 0o755)


def get_project_dir(project_id: str) -> Path:
    """Get project directory path"""
    return PROJECTS_DIR / project_id


def get_project_metadata_file(project_id: str) -> Path:
    """Get project metadata file path"""
    return get_project_dir(project_id) / PROJECT_METADATA_FILE


def get_project_dashboard_file(project_id: str) -> Path:
    """Get project dashboard file path"""
    return get_project_dir(project_id) / DASHBOARD_FILE


def get_project_log_dir(project_id: str) -> Path:
    """Get project logs directory"""
    return get_project_dir(project_id) / "logs"


def get_stage_log_file(project_id: str, stage: str) -> Path:
    """Get log file path for a specific stage"""
    return get_project_log_dir(project_id) / f"{stage}.log"


# Initialize on import
ensure_directories()
