"""
NGS Pipeline Web Wrapper - FastAPI Backend
Main application for queue monitoring, project management, and pipeline orchestration.
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import subprocess
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DATA_DIR = Path("/app/data")
INPUT_QUEUE_DIR = BASE_DATA_DIR / "input_queue"
PROJECTS_DIR = BASE_DATA_DIR / "projects"
SCRIPTS_DIR = Path("/app/scripts")

# Ensure directories exist
INPUT_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# Pipeline stages in order
PIPELINE_STAGES = [
    "getting_data",
    "fastqc_raw",
    "trimming",
    "fastqc_trim",
    "multiqc_raw",
    "multiqc_trim",
    "reference",
    "bwa_alignment",
    "samtools_sort",
    "variant_calling",
    "consensus",
    "cds_extraction"
]

# Project status enum
class ProjectStatus:
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ProjectMetadata:
    """Manages project metadata and state"""
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.project_dir = PROJECTS_DIR / project_id
        self.metadata_file = self.project_dir / "metadata.json"
        self.logs_dir = self.project_dir / "logs"
        
    def create(self, input_files: List[str]) -> Dict:
        """Create a new project"""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        metadata = {
            "project_id": self.project_id,
            "status": ProjectStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "input_files": input_files,
            "stages": {stage: {"status": "pending", "started_at": None, "completed_at": None, "log_file": None} 
                      for stage in PIPELINE_STAGES}
        }
        
        # Create subdirectories
        (self.project_dir / "inputs").mkdir(exist_ok=True)
        (self.project_dir / "outputs").mkdir(exist_ok=True)
        (self.project_dir / "artifacts").mkdir(exist_ok=True)
        
        self.save(metadata)
        return metadata
    
    def load(self) -> Dict:
        """Load project metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save(self, metadata: Dict):
        """Save project metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def update_stage(self, stage: str, status: str, log_file: Optional[str] = None):
        """Update stage status"""
        metadata = self.load()
        if stage in metadata["stages"]:
            stage_info = metadata["stages"][stage]
            stage_info["status"] = status
            
            if status == "running" and not stage_info["started_at"]:
                stage_info["started_at"] = datetime.now().isoformat()
            elif status in ["completed", "failed"]:
                stage_info["completed_at"] = datetime.now().isoformat()
            
            if log_file:
                stage_info["log_file"] = log_file
        
        # Update overall project status
        if status == "running" and metadata["status"] != "running":
            metadata["status"] = "running"
            metadata["started_at"] = datetime.now().isoformat()
        
        self.save(metadata)


class InputQueueWatcher(FileSystemEventHandler):
    """Watches for new files in the input queue"""
    def __init__(self, app_context):
        self.app = app_context
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        # Check if it's a relevant file
        if self._is_relevant_file(event.src_path):
            logger.info(f"New file detected: {event.src_path}")
            # Auto-create project or notify
            asyncio.create_task(self._handle_new_file(event.src_path))
    
    @staticmethod
    def _is_relevant_file(filepath: str) -> bool:
        """Check if file is FASTQ, SRA list, or other relevant format"""
        valid_extensions = {'.fastq', '.fq', '.fastq.gz', '.fq.gz', '.txt', '.sra', '.csv'}
        return any(filepath.lower().endswith(ext) for ext in valid_extensions)
    
    async def _handle_new_file(self, filepath: str):
        """Handle new file detection"""
        try:
            await asyncio.sleep(1)  # Wait for file to be fully written
            logger.info(f"Processing new file: {filepath}")
        except Exception as e:
            logger.error(f"Error handling new file {filepath}: {e}")


# FastAPI Application
app = FastAPI(
    title="NGS Pipeline Web Wrapper",
    description="Web interface for NGS pipeline queue management and execution",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File watcher
observer = Observer()
watcher = InputQueueWatcher(app)
observer.schedule(watcher, str(INPUT_QUEUE_DIR), recursive=False)


@app.on_event("startup")
async def startup_event():
    """Startup event - initialize watcher"""
    observer.start()
    logger.info("Input queue watcher started")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup"""
    observer.stop()
    observer.join()
    logger.info("Input queue watcher stopped")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Redirect to dashboard"""
    return {"message": "NGS Pipeline Web Wrapper API", "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "input_queue": INPUT_QUEUE_DIR.exists(),
        "projects_dir": PROJECTS_DIR.exists(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    projects = []
    if PROJECTS_DIR.exists():
        for project_dir in PROJECTS_DIR.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    projects.append(metadata)
    
    return {"projects": projects, "count": len(projects)}


@app.post("/api/projects/create")
async def create_project(background_tasks: BackgroundTasks):
    """Create a new project from input queue"""
    # Get files from input queue
    input_files = []
    if INPUT_QUEUE_DIR.exists():
        input_files = [f.name for f in INPUT_QUEUE_DIR.iterdir() if f.is_file()]
    
    if not input_files:
        raise HTTPException(status_code=400, detail="No files in input queue")
    
    # Generate project ID
    project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Create project
    meta = ProjectMetadata(project_id)
    metadata = meta.create(input_files)
    
    # Move files to project inputs
    for file in input_files:
        src = INPUT_QUEUE_DIR / file
        dst = meta.project_dir / "inputs" / file
        if src.exists():
            src.rename(dst)
            logger.info(f"Moved {file} to project {project_id}")
    
    logger.info(f"Created project: {project_id}")
    return {"project_id": project_id, "metadata": metadata}


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    meta = ProjectMetadata(project_id)
    metadata = meta.load()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return metadata


@app.post("/api/projects/{project_id}/execute")
async def execute_project(project_id: str, background_tasks: BackgroundTasks):
    """Execute pipeline for a project"""
    meta = ProjectMetadata(project_id)
    metadata = meta.load()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if metadata["status"] == "running":
        raise HTTPException(status_code=400, detail="Project is already running")
    
    # Schedule pipeline execution
    background_tasks.add_task(execute_pipeline, project_id)
    
    # Update status
    meta.update_stage("initialization", "scheduled")
    
    return {"status": "execution_scheduled", "project_id": project_id}


@app.get("/api/projects/{project_id}/status")
async def get_project_status(project_id: str):
    """Get real-time project status"""
    meta = ProjectMetadata(project_id)
    metadata = meta.load()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Enrich with log info
    for stage, info in metadata["stages"].items():
        log_file = info.get("log_file")
        if log_file and Path(log_file).exists():
            with open(log_file, 'r') as f:
                info["recent_logs"] = f.readlines()[-20:]  # Last 20 lines
    
    return metadata


@app.get("/api/projects/{project_id}/logs/{stage}")
async def get_stage_logs(project_id: str, stage: str):
    """Get logs for a specific stage"""
    meta = ProjectMetadata(project_id)
    metadata = meta.load()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stage_info = metadata["stages"].get(stage)
    if not stage_info:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    log_file = stage_info.get("log_file")
    if not log_file or not Path(log_file).exists():
        return {"logs": [], "stage": stage, "status": stage_info["status"]}
    
    with open(log_file, 'r') as f:
        logs = f.readlines()
    
    return {"logs": logs, "stage": stage, "status": stage_info["status"]}


@app.get("/api/projects/{project_id}/artifacts")
async def list_artifacts(project_id: str):
    """List project artifacts"""
    meta = ProjectMetadata(project_id)
    artifacts_dir = meta.project_dir / "artifacts"
    
    artifacts = []
    if artifacts_dir.exists():
        for item in artifacts_dir.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(artifacts_dir)
                artifacts.append({
                    "name": str(relative_path),
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    "path": f"/api/projects/{project_id}/artifacts/{quote(str(relative_path))}"
                })
    
    return {"artifacts": artifacts, "count": len(artifacts)}


@app.get("/api/projects/{project_id}/artifacts/{file_path:path}")
async def download_artifact(project_id: str, file_path: str):
    """Download a specific artifact"""
    meta = ProjectMetadata(project_id)
    full_path = meta.project_dir / "artifacts" / file_path
    
    # Security check
    if not full_path.resolve().is_relative_to(meta.project_dir.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return FileResponse(full_path)


@app.get("/projects/{project_id}/")
async def get_dashboard(project_id: str):
    """Serve project dashboard"""
    meta = ProjectMetadata(project_id)
    metadata = meta.load()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Project not found")
    
    dashboard_file = meta.project_dir / "index.html"
    if dashboard_file.exists():
        with open(dashboard_file, 'r') as f:
            return HTMLResponse(content=f.read())
    
    # Generate dashboard if not exists
    dashboard_html = generate_dashboard(project_id, metadata)
    return HTMLResponse(content=dashboard_html)


@app.get("/projects/{project_id}/index.html")
async def get_dashboard_file(project_id: str):
    """Serve dashboard HTML file"""
    meta = ProjectMetadata(project_id)
    dashboard_file = meta.project_dir / "index.html"
    
    if not dashboard_file.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    return FileResponse(dashboard_file)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_dashboard(project_id: str, metadata: Dict) -> str:
    """Generate HTML dashboard for a project"""
    from templates.dashboard_template import get_dashboard_html
    
    html = get_dashboard_html(project_id, metadata)
    
    # Save to file
    meta = ProjectMetadata(project_id)
    dashboard_file = meta.project_dir / "index.html"
    with open(dashboard_file, 'w') as f:
        f.write(html)
    
    return html


async def execute_pipeline(project_id: str):
    """Execute NGS pipeline for a project"""
    meta = ProjectMetadata(project_id)
    metadata = meta.load()
    
    logger.info(f"Starting pipeline execution for project {project_id}")
    
    try:
        # Get input files
        inputs_dir = meta.project_dir / "inputs"
        input_files = list(inputs_dir.glob("*"))
        
        if not input_files:
            logger.warning(f"No input files for project {project_id}")
            meta.update_stage("initialization", "failed")
            return
        
        # Execute stages sequentially
        for stage in PIPELINE_STAGES:
            logger.info(f"Executing stage: {stage}")
            meta.update_stage(stage, "running")
            
            # Create log file
            log_file = meta.logs_dir / f"{stage}.log"
            meta.update_stage(stage, "running", str(log_file))
            
            try:
                # Execute stage script
                result = await execute_stage(stage, meta, log_file)
                
                if result.returncode == 0:
                    meta.update_stage(stage, "completed")
                    logger.info(f"Stage {stage} completed successfully")
                else:
                    meta.update_stage(stage, "failed")
                    logger.error(f"Stage {stage} failed with return code {result.returncode}")
                    break
            
            except Exception as e:
                logger.error(f"Error executing stage {stage}: {e}")
                meta.update_stage(stage, "failed")
                break
        
        # Update final status
        metadata = meta.load()
        all_completed = all(s["status"] == "completed" for s in metadata["stages"].values())
        
        if all_completed:
            metadata["status"] = ProjectStatus.COMPLETED
            metadata["completed_at"] = datetime.now().isoformat()
        else:
            metadata["status"] = ProjectStatus.FAILED
            metadata["completed_at"] = datetime.now().isoformat()
        
        meta.save(metadata)
        logger.info(f"Pipeline execution finished for project {project_id}")
        
        # Regenerate dashboard
        generate_dashboard(project_id, metadata)
    
    except Exception as e:
        logger.error(f"Fatal error in pipeline execution for {project_id}: {e}")
        meta.update_stage("initialization", "failed")


async def execute_stage(stage: str, meta: ProjectMetadata, log_file: Path) -> subprocess.CompletedProcess:
    """Execute a pipeline stage"""
    script_path = SCRIPTS_DIR / f"{stage}.sh"
    
    if not script_path.exists():
        raise FileNotFoundError(f"Stage script not found: {script_path}")
    
    # Prepare environment
    env = os.environ.copy()
    env["PROJECT_DIR"] = str(meta.project_dir)
    env["INPUTS_DIR"] = str(meta.project_dir / "inputs")
    env["OUTPUTS_DIR"] = str(meta.project_dir / "outputs")
    env["ARTIFACTS_DIR"] = str(meta.project_dir / "artifacts")
    env["LOGS_DIR"] = str(meta.logs_dir)
    
    # Execute script
    result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(meta.project_dir)
    )
    
    # Write logs
    with open(log_file, 'w') as f:
        f.write(f"=== {stage} - {datetime.now().isoformat()} ===\n")
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\n\nSTDERR:\n")
        f.write(result.stderr)
        f.write(f"\n\nReturn code: {result.returncode}\n")
    
    return result


# ============================================================================
# STATIC FILES
# ============================================================================

# Serve static files if they exist
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
