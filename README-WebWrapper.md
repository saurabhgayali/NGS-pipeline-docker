# NGS Pipeline Web Wrapper - Deployment Guide

## Overview

This is a production-ready containerized web application wrapper for the NGS (Next-Generation Sequencing) pipeline. It provides:

- **FastAPI-based Web Server** for queue management and status tracking
- **Input Directory Monitoring** - automatically detect new FASTQ/SRA files
- **Project-based Isolation** - each batch of samples gets its own project directory
- **Interactive Status Dashboard** - real-time pipeline execution monitoring
- **Log Streaming** - live access to per-stage logs
- **Artifact Management** - organized output files with download links
- **Docker Container** - production-ready with all bioinformatics dependencies
- **Docker Compose** - simplified deployment with volume management
- **Nginx Reverse Proxy** - optional production web server

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Container                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Web Application                │  │
│  │  - Queue Engine & File Monitoring                   │  │
│  │  - Project Management & Status Tracking             │  │
│  │  - Dashboard Generation & Serving                   │  │
│  │  - API Endpoints for Status & Logs                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Conda Environment (bioinformatics)           │  │
│  │  - sra-tools, fastqc, fastq-dump                    │  │
│  │  - bwa, samtools, bcftools                          │  │
│  │  - multiqc, trimmomatic, biopython                  │  │
│  │  - pyliftover for coordinate transformation         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
            ↓                              ↓
    ┌───────────────┐            ┌───────────────────┐
    │ Input Queue   │            │ Projects & Results│
    │ (/app/data/   │            │ (/app/data/       │
    │  input_queue) │            │  projects)        │
    └───────────────┘            └───────────────────┘
```

## Directory Structure

```
NGS-pipeline-docker/
├── Dockerfile                      # Production container image
├── docker-compose.yml              # Orchestration configuration
├── nginx/
│   └── nginx.conf                  # Reverse proxy configuration (optional)
├── webapp/                         # Web application code
│   ├── app/
│   │   └── main.py               # FastAPI application
│   ├── templates/
│   │   └── dashboard_template.py  # Dashboard HTML generation
│   └── requirements.txt           # Python dependencies
├── wrapper_scripts/
│   └── execute_stage.sh           # Pipeline stage executor
├── scripts/                        # Original NGS pipeline scripts
│   ├── config.sh
│   ├── getting_data.sh
│   ├── fastqc_trim.sh
│   ├── trimming.sh
│   ├── bwa_alignment.sh
│   └── ... (other pipeline stages)
├── python_scripts/
│   └── cds_extraction.py
├── data/
│   ├── input_queue/              # New files placed here
│   ├── projects/                 # All project data stored here
│   └── reference/                # Reference genome files
└── README-WebWrapper.md           # This file
```

## Quick Start

### Prerequisites

- Docker & Docker Compose installed
- At least 4GB RAM, 20GB disk space recommended
- Linux/macOS or WSL2 (Windows)

### 1. Clone Repository

```bash
git clone https://github.com/saurabhgayali/NGS-pipeline-docker.git
cd NGS-pipeline-docker
```

### 2. Prepare Data Directories

```bash
# Create required directories
mkdir -p data/input_queue
mkdir -p data/projects
mkdir -p data/raw_reads
mkdir -p data/reference

# Place reference genome in data/reference/
# (must contain TB reference H37Rv or your chosen reference)
```

### 3. Build and Run Container

**Option A: Using Docker Compose (Recommended)**

```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f ngs-pipeline-web

# Stop the container
docker-compose down
```

**Option B: Using Docker CLI**

```bash
# Build the image
docker build -t ngs-pipeline-web:latest .

# Run the container
docker run -d \
  --name ngs-pipeline-web \
  -p 7860:7860 \
  -v $(pwd)/data/input_queue:/app/data/input_queue \
  -v $(pwd)/data/projects:/app/data/projects \
  -v $(pwd)/data/reference:/app/data/reference:ro \
  -v $(pwd)/data/raw_reads:/app/data/raw_reads \
  -v $(pwd)/scripts:/app/scripts:ro \
  -v $(pwd)/metadata:/app/metadata:ro \
  -e PORT=7860 \
  ngs-pipeline-web:latest

# View logs
docker logs -f ngs-pipeline-web

# Stop the container
docker stop ngs-pipeline-web
docker rm ngs-pipeline-web
```

### 4. Access the Web Interface

Open your browser and navigate to:
- **Dashboard**: http://localhost:7860/
- **API Docs**: http://localhost:7860/docs
- **Health Check**: http://localhost:7860/api/health

## Usage Workflow

### Step 1: Place Input Files

Place your input files in the `data/input_queue/` directory:

```bash
# Option A: FASTQ files
cp sample_1.fastq.gz data/input_queue/
cp sample_2.fastq.gz data/input_queue/

# Option B: SRA Accession IDs (as text file)
echo "SRR1234567" > data/input_queue/accessions.txt
echo "SRR1234568" >> data/input_queue/accessions.txt
```

### Step 2: Create Project via Web UI

1. Open http://localhost:7860 in browser
2. Click "Create Project" or use API endpoint:

```bash
curl -X POST http://localhost:7860/api/projects/create
```

### Step 3: Monitor Execution

1. View project dashboard at: `http://localhost:7860/projects/<project_id>/`
2. Check real-time status for each pipeline stage
3. View logs by clicking "View Logs" on any stage
4. Download artifacts as they complete

### Step 4: Access Results

All results are stored in:
```
data/projects/<project_id>/
├── inputs/           # Input FASTQ/SRA files
├── outputs/          # Intermediate and final outputs
├── logs/             # Per-stage log files
├── artifacts/        # Final deliverables (MultiQC, CDS, etc)
└── index.html        # Dashboard (also served via web)
```

## API Endpoints

### Core Project Endpoints

```bash
# List all projects
GET /api/projects

# Create new project from input queue
POST /api/projects/create

# Get project details
GET /api/projects/{project_id}

# Get project status
GET /api/projects/{project_id}/status

# Start pipeline execution
POST /api/projects/{project_id}/execute
```

### Logs & Monitoring

```bash
# Get logs for specific stage
GET /api/projects/{project_id}/logs/{stage}

# Get all artifacts
GET /api/projects/{project_id}/artifacts

# Download specific artifact
GET /api/projects/{project_id}/artifacts/{file_path}
```

### System Endpoints

```bash
# Health check
GET /api/health

# Dashboard HTML (served by web server)
GET /projects/{project_id}/
GET /projects/{project_id}/index.html
```

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `7860` | Web server port |
| `PROJECT_DIR` | Auto-set | Project directory path |
| `INPUTS_DIR` | `{PROJECT_DIR}/inputs` | Input files directory |
| `OUTPUTS_DIR` | `{PROJECT_DIR}/outputs` | Pipeline outputs directory |
| `ARTIFACTS_DIR` | `{PROJECT_DIR}/artifacts` | Final artifacts directory |
| `LOGS_DIR` | `{PROJECT_DIR}/logs` | Log files directory |

### Pipeline Configuration

Edit `scripts/config.sh` to customize:
- Reference genome path
- Output directory structure
- Thread count for parallel processing
- Tool-specific parameters

## Volume Mounts

| Host Path | Container Path | Read-Only | Purpose |
|-----------|----------------|-----------|---------|
| `./data/input_queue` | `/app/data/input_queue` | No | Input file monitoring |
| `./data/projects` | `/app/data/projects` | No | Project data & results |
| `./scripts` | `/app/scripts` | Yes | Pipeline scripts |
| `./data/reference` | `/app/data/reference` | Yes | Reference genome |
| `./data/raw_reads` | `/app/data/raw_reads` | No | Raw sequencing data |
| `./metadata` | `/app/metadata` | Yes | Sample metadata |

## Production Deployment

### Using Nginx Reverse Proxy

Uncomment the nginx service in `docker-compose.yml`:

```bash
docker-compose --profile prod up -d
```

This adds:
- Nginx reverse proxy on port 80/443
- SSL/TLS support
- Gzip compression
- Static file caching
- Security headers

### Enable SSL/TLS

1. Generate certificates:
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

2. Uncomment SSL sections in `nginx/nginx.conf`

3. Update nginx.conf with your domain name

### Resource Limits

Uncomment in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      cpus: '2'
      memory: 4G
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs ngs-pipeline-web

# Verify directories exist
ls -la data/input_queue data/projects

# Check Docker daemon
docker ps

# Rebuild image
docker-compose build --no-cache
```

### Pipeline stage fails

1. Check logs in web dashboard: "View Logs" button on failed stage
2. Verify input files in `data/projects/<project_id>/inputs/`
3. Check reference genome path in `scripts/config.sh`
4. Review stage-specific log file: `data/projects/<project_id>/logs/{stage}.log`

### No files detected

1. Ensure files in `data/input_queue/` are readable
2. Check file permissions: `chmod 644 data/input_queue/*`
3. Verify file extensions (.fastq, .fq, .fastq.gz, .txt)
4. Check container volume mounts: `docker inspect ngs-pipeline-web`

### Slow performance

1. Check system resources: `docker stats`
2. Monitor container logs for bottlenecks
3. Adjust thread count in `scripts/config.sh` (THREADS=8)
4. Increase resource limits in docker-compose.yml

### Dashboard not updating

1. Check API endpoint: `curl http://localhost:7860/api/health`
2. Verify project exists: `curl http://localhost:7860/api/projects`
3. Check browser console for JavaScript errors (F12)
4. Clear browser cache and refresh

## Implementation Details

### Project Lifecycle

1. **Detection** → Files placed in `input_queue/`
2. **Creation** → Project directory created with metadata.json
3. **Initialization** → Files moved to project/inputs/, directories created
4. **Execution** → Pipeline stages run sequentially with log tracking
5. **Monitoring** → Dashboard updates in real-time
6. **Completion** → Results stored in project/artifacts/, dashboard finalized

### Status Tracking

Each pipeline stage has status:
- **pending** → Waiting to run
- **running** → Currently executing
- **completed** → Finished successfully
- **failed** → Error occurred, check logs

Overall project status:
- **pending** → Initial state
- **running** → At least one stage is running
- **completed** → All stages succeeded
- **failed** → One or more stages failed

### Log Files

Per-stage logs stored at:
```
data/projects/<project_id>/logs/
├── getting_data.log
├── fastqc_raw.log
├── trimming.log
├── fastqc_trim.log
├── multiqc_raw.log
├── multiqc_trim.log
├── reference.log
├── bwa_alignment.log
├── samtools_sort.log
├── variant_calling.log
├── consensus.log
└── cds_extraction.log
```

Each log contains stdout, stderr, and return code.

## Performance Benchmarks

Typical execution times (per-sample, 8 threads):

| Stage | Time | Notes |
|-------|------|-------|
| Data Download | 30-60 min | Depends on SRA size |
| FastQC | 2-5 min | Per sample |
| Trimming | 5-10 min | Trimmomatic PE |
| Alignment | 10-20 min | BWA MEM to 4.4Mb reference |
| Sorting | 2-5 min | samtools sort + index |
| Variant Calling | 5-15 min | bcftools mpileup + call |
| Consensus | 1-2 min | bcftools consensus |
| CDS Extraction | 1-2 min | Biopython + pyliftover |
| **Total** | **~2-3 hours** | For 100M read pair sample |

## Advanced Features

### Custom Pipeline Stages

Modify `webapp/app/main.py`:

```python
PIPELINE_STAGES = [
    "getting_data",
    "custom_stage",  # Add your stage here
    "fastqc_raw",
    # ... rest of stages
]
```

Create corresponding script in `wrapper_scripts/`.

### Integration with External Tools

Pass environment variables through `docker run`:

```bash
docker run -e REFERENCE_DB=/path/to/db \
           -v /external/db:/app/external/db:ro \
           ngs-pipeline-web:latest
```

### Scaling with Kubernetes

Example deployment manifest in `k8s/` directory (optional).

## Support & Contribution

For issues, feature requests, or contributions:

1. Check existing issues on GitHub
2. Review logs in `data/projects/<project_id>/logs/`
3. Test with provided example data
4. File issue with logs and minimal reproduction case

## License

Same as original NGS-pipeline-docker repository

## Citation

If using in research, please cite:
- Original pipeline repository
- This web wrapper implementation
- Docker & dependencies versions

## Changelog

### v1.0.0 (Current)
- Initial release
- FastAPI web server
- File queue monitoring
- Project management
- Dashboard generation
- Docker containerization
- Nginx reverse proxy support

## Contact

For questions about the web wrapper implementation, contact: [Your Contact Info]
For original pipeline questions, see: https://github.com/saurabhgayali/NGS-pipeline-docker
