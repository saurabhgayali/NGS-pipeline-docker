# NGS Pipeline Web Wrapper - API Documentation

## Base URL

```
http://localhost:7860/api
```

## Authentication

Currently, no authentication is required. For production, add JWT or API key authentication.

---

## Endpoints

### Health & System

#### Check API Health
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "input_queue": true,
  "projects_dir": true,
  "timestamp": "2026-08-30T16:32:32.131+00:00"
}
```

---

### Project Management

#### List All Projects
```http
GET /api/projects
```

**Response:**
```json
{
  "projects": [
    {
      "project_id": "project_20260830_163232_abc12345",
      "status": "running",
      "created_at": "2026-08-30T16:32:32.131+00:00",
      "started_at": "2026-08-30T16:32:45.000+00:00",
      "completed_at": null,
      "input_files": ["sample_1.fastq.gz", "sample_2.fastq.gz"],
      "stages": {...}
    }
  ],
  "count": 1
}
```

#### Create New Project
```http
POST /api/projects/create
```

**Description:** Creates a new project from files in the input queue directory.

**Response:**
```json
{
  "project_id": "project_20260830_163232_abc12345",
  "metadata": {
    "project_id": "project_20260830_163232_abc12345",
    "status": "pending",
    "created_at": "2026-08-30T16:32:32.131+00:00",
    "started_at": null,
    "completed_at": null,
    "input_files": ["sample_1.fastq.gz"],
    "stages": {
      "getting_data": {"status": "pending", ...},
      "fastqc_raw": {"status": "pending", ...},
      ...
    }
  }
}
```

**Errors:**
- `400 Bad Request` - No files in input queue

#### Get Project Details
```http
GET /api/projects/{project_id}
```

**Parameters:**
- `project_id` (string, required) - Unique project identifier

**Response:**
```json
{
  "project_id": "project_20260830_163232_abc12345",
  "status": "running",
  "created_at": "2026-08-30T16:32:32.131+00:00",
  "started_at": "2026-08-30T16:32:45.000+00:00",
  "completed_at": null,
  "input_files": ["sample_1.fastq.gz"],
  "stages": {
    "getting_data": {
      "status": "completed",
      "started_at": "2026-08-30T16:32:45.000+00:00",
      "completed_at": "2026-08-30T16:35:12.000+00:00",
      "log_file": "/app/data/projects/project_20260830_163232_abc12345/logs/getting_data.log"
    },
    "fastqc_raw": {
      "status": "running",
      "started_at": "2026-08-30T16:35:13.000+00:00",
      "completed_at": null,
      "log_file": "/app/data/projects/project_20260830_163232_abc12345/logs/fastqc_raw.log"
    },
    ...
  }
}
```

**Errors:**
- `404 Not Found` - Project does not exist

---

### Project Execution

#### Get Project Status
```http
GET /api/projects/{project_id}/status
```

**Description:** Get real-time project status including recent logs.

**Parameters:**
- `project_id` (string, required) - Unique project identifier

**Response:**
```json
{
  "project_id": "project_20260830_163232_abc12345",
  "status": "running",
  "stages": {
    "getting_data": {
      "status": "completed",
      "started_at": "2026-08-30T16:32:45.000+00:00",
      "completed_at": "2026-08-30T16:35:12.000+00:00",
      "recent_logs": ["Log line 1", "Log line 2", ...]
    },
    ...
  }
}
```

#### Execute Project Pipeline
```http
POST /api/projects/{project_id}/execute
```

**Description:** Start pipeline execution for a project.

**Parameters:**
- `project_id` (string, required) - Unique project identifier

**Response:**
```json
{
  "status": "execution_scheduled",
  "project_id": "project_20260830_163232_abc12345"
}
```

**Errors:**
- `404 Not Found` - Project does not exist
- `400 Bad Request` - Project is already running

---

### Logs & Monitoring

#### Get Stage Logs
```http
GET /api/projects/{project_id}/logs/{stage}
```

**Description:** Retrieve full log file for a specific pipeline stage.

**Parameters:**
- `project_id` (string, required) - Unique project identifier
- `stage` (string, required) - Stage name (getting_data, fastqc_raw, trimming, etc.)

**Response:**
```json
{
  "logs": [
    "=== getting_data - 2026-08-30T16:32:45.000+00:00 ===",
    "STDOUT:",
    "Isolating the SRA ids...",
    "",
    "Saved the Sensitive accession ids...",
    "STDERR:",
    "...",
    "Return code: 0"
  ],
  "stage": "getting_data",
  "status": "completed"
}
```

**Available Stages:**
- getting_data
- fastqc_raw
- trimming
- fastqc_trim
- multiqc_raw
- multiqc_trim
- reference
- bwa_alignment
- samtools_sort
- variant_calling
- consensus
- cds_extraction

**Errors:**
- `404 Not Found` - Project or stage not found

---

### Artifacts

#### List Project Artifacts
```http
GET /api/projects/{project_id}/artifacts
```

**Description:** List all output artifacts from pipeline execution.

**Parameters:**
- `project_id` (string, required) - Unique project identifier

**Response:**
```json
{
  "artifacts": [
    {
      "name": "multiqc_report/multiqc.html",
      "size": 2048576,
      "modified": "2026-08-30T16:45:30.000+00:00",
      "path": "/api/projects/project_20260830_163232_abc12345/artifacts/multiqc_report%2Fmultiqc.html"
    },
    {
      "name": "cds/rpoB.fasta",
      "size": 2048,
      "modified": "2026-08-30T17:00:15.000+00:00",
      "path": "/api/projects/project_20260830_163232_abc12345/artifacts/cds%2FrpoB.fasta"
    },
    ...
  ],
  "count": 10
}
```

#### Download Artifact
```http
GET /api/projects/{project_id}/artifacts/{file_path}
```

**Description:** Download a specific artifact file.

**Parameters:**
- `project_id` (string, required) - Unique project identifier
- `file_path` (string, required) - Relative path to artifact file (URL-encoded)

**Example:**
```bash
# Download: cds/rpoB.fasta
GET /api/projects/project_20260830_163232_abc12345/artifacts/cds%2FrpoB.fasta
```

**Response:** Binary file data

**Errors:**
- `404 Not Found` - Artifact not found
- `403 Forbidden` - Access denied (path traversal attempt)

---

### Dashboards

#### Get Project Dashboard
```http
GET /projects/{project_id}/
GET /projects/{project_id}/index.html
```

**Description:** Serve the interactive HTML dashboard for a project.

**Parameters:**
- `project_id` (string, required) - Unique project identifier

**Response:** HTML content with embedded CSS and JavaScript

**Features:**
- Real-time status updates
- Live log viewer
- Artifact browser
- Download links
- Timeline visualization

**Errors:**
- `404 Not Found` - Project not found

---

## Status Values

### Project Status
- **pending** - Initial state, awaiting execution
- **initializing** - Setting up project directories
- **running** - Pipeline is executing
- **completed** - All stages finished successfully
- **failed** - One or more stages failed
- **paused** - Execution paused (for future enhancement)

### Stage Status
- **pending** - Waiting to run
- **running** - Currently executing
- **completed** - Finished successfully
- **failed** - Error occurred

---

## Pipeline Stages

| Order | Stage | Description |
|-------|-------|-------------|
| 1 | getting_data | Download SRA files & convert to FASTQ |
| 2 | fastqc_raw | Quality control on raw reads |
| 3 | trimming | Adapter & quality trimming |
| 4 | fastqc_trim | Quality control on trimmed reads |
| 5 | multiqc_raw | Aggregate raw QC report |
| 6 | multiqc_trim | Aggregate trimmed QC report |
| 7 | reference | Index reference genome |
| 8 | bwa_alignment | Align reads to reference |
| 9 | samtools_sort | Sort and index BAM files |
| 10 | variant_calling | Call variants |
| 11 | consensus | Generate consensus sequences |
| 12 | cds_extraction | Extract coding sequences |

---

## Error Handling

All errors return JSON with the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 500 | Server Error - Internal error |
| 503 | Service Unavailable - Server offline |

---

## Usage Examples

### cURL Examples

**Create a project:**
```bash
curl -X POST http://localhost:7860/api/projects/create
```

**Get project status:**
```bash
curl http://localhost:7860/api/projects/project_20260830_163232_abc12345
```

**View stage logs:**
```bash
curl http://localhost:7860/api/projects/project_20260830_163232_abc12345/logs/fastqc_raw
```

**List artifacts:**
```bash
curl http://localhost:7860/api/projects/project_20260830_163232_abc12345/artifacts
```

**Download artifact:**
```bash
curl -O http://localhost:7860/api/projects/project_20260830_163232_abc12345/artifacts/cds%2FrpoB.fasta
```

### Python Examples

See `client.py` in repository root for complete Python API client.

```python
from client import NGSPipelineClient

# Initialize client
client = NGSPipelineClient("http://localhost:7860")

# Check health
health = client.health_check()

# Create project
project = client.create_project()
project_id = project['project_id']

# Execute pipeline
client.execute_project(project_id)

# Wait for completion
result = client.wait_for_completion(project_id, timeout=86400)

# Download results
artifacts = client.list_artifacts(project_id)
for artifact in artifacts['artifacts']:
    client.download_artifact(project_id, artifact['name'], f"./{artifact['name']}")
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, add rate limiting to:
- Prevent abuse
- Manage server resources
- Fair allocation of computation time

Recommended: 100 requests/minute per IP address

---

## Pagination

List endpoints support pagination (future enhancement):

```
GET /api/projects?page=1&per_page=10
GET /api/projects/{project_id}/artifacts?page=1&per_page=50
```

Currently returns all results; pagination will be added in future versions.

---

## Webhooks

Webhook support for pipeline events (future enhancement):

```
POST /api/webhooks/register
{
  "event": "stage_completed",
  "url": "https://your-server.com/callback",
  "secret": "webhook_secret"
}
```

---

## Versioning

API version: 1.0.0

Current API is stable. Version changes will be announced and old versions maintained for 6 months.

Future versions will use URL prefix: `/api/v2/`, etc.

---

## Support & Documentation

- **Interactive API Docs** (Swagger UI): http://localhost:7860/docs
- **Alternative API Docs** (ReDoc): http://localhost:7860/redoc
- **GitHub Repository**: https://github.com/saurabhgayali/NGS-pipeline-docker
- **Issue Tracker**: GitHub Issues
