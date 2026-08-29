Act as an expert Systems & Bioinformatics Software Engineer. 

I want to advance my fork of an NGS (Next-Generation Sequencing) processing pipeline repository. The original repository consists of modular Bash and Python scripts designed to process raw sequencing reads (SRA/FASTQ) through quality control, alignment, variant calling, consensus generation, and CDS extraction.

Generate the code, project structure, and implementation details for a containerized Web application wrapper based on the specifications below:

### 1. Web Frontend & Queue Engine (Python/Docker)
* Build a lightweight Web UI and queue engine (using FastAPI + HTML/JS or Streamlit/Gradio).
* **Input Directory Monitoring:** The app must actively scan a designated host symlink folder (`/app/data/input_queue`) for new files (e.g., FASTQ, FASTQ.GZ, or text files containing SRA Accession IDs).
* **Project Creation Automation:**
  * When new files are detected, automatically (or upon user confirmation via Web UI) generate an isolated Project Directory under the output symlink path (`/app/data/projects/<project_id>/`).
  * Move the detected input files from `/app/data/input_queue` into `/app/data/projects/<project_id>/inputs/`, leaving the input symlink clean/empty for new incoming batches.
  * Trigger the execution of the NGS shell scripts sequentially, directing all logs, intermediate data, and final results strictly into that project's folder.

### 2. Static Status Dashboard (`index.html`) & Web Serving
* **Interactive Status Page:** For every project created, automatically generate and update an `index.html` file directly inside `/app/data/projects/<project_id>/index.html`.
* **Dashboard Features:**
  * Real-time execution status (Pending, Running, Completed, Failed) for each pipeline stage (QC, Trimming, Alignment, Variant Calling, CDS Extraction).
  * Live stdout/stderr log viewer reading from per-stage log files.
  * Direct web links to view or download final generated artifacts (e.g., MultiQC HTML reports, extracted CDS FASTA files).
* **HTTP Serving:** The Web app container must serve these generated `index.html` dashboards and project artifacts over HTTP, while ensuring the underlying files remain directly readable and accessible on the host filesystem via the output volume/symlink mount.

### 3. Comprehensive Dockerfile & Container Architecture
* Create a production-ready `Dockerfile` based on `ubuntu:24.04`.
* **Dependencies:**
  * Install Conda/Miniconda and create an environment containing all necessary bioconda/conda-forge tools (`sra-tools`, `fastqc`, `trimmomatic`, `multiqc`, `bwa`, `samtools`, `bcftools`, `biopython`).
  * Install Python dependencies (`pyliftover`, web server dependencies like `fastapi`, `uvicorn`, `jinja2`, or `streamlit`).
* **Storage & Networking:**
  * Expose an environment variable `PORT` (default: `7860`) for the web server.
  * Define explicit volume mount points for input and output symlink directories (`/app/data/input_queue` and `/app/data/projects`).
* Provide a `docker-compose.yml` or standard `docker run` command demonstrating how to run the container with host path mounts.

Please output the complete, modular code structure, script modifications, Web app code, `index.html` dashboard template, and `Dockerfile` ready for implementation.
