import shutil
import uuid
import zipfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Clean Architecture Imports
from src.md_analysis.infrastructure.plotting.metrics import METRIC_MAP
from src.md_analysis.infrastructure.persistence.local_storage import (
    save_job_status, load_all_jobs, get_job_path, delete_job_record, cleanup_old_jobs, STORAGE_BASE
)
from src.md_analysis.application.analysis_worker import run_analysis_task

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Clean old files
    print("Iniciando limpieza de archivos temporales...")
    cleanup_old_jobs(max_age_hours=2)
    yield
    # Shutdown logic (optional)
    pass

app = FastAPI(
    title="VIZO - MD Analysis Professional Backend",
    description="Asynchronous Local Backend with Job Tracking",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # More permissive for local use
    allow_methods=["*"],
    allow_headers=["*"],
)

def detect_metric(filename: str) -> str:
    for metric_name, plotter in METRIC_MAP.items():
        if filename.endswith(plotter.suffix):
            return metric_name
    expected = [p.suffix for p in METRIC_MAP.values()]
    raise HTTPException(
        status_code=400,
        detail=f"Métrica no detectada en '{filename}'. Debe terminar en: {', '.join(expected)}"
    )

@app.get("/health")
def health():
    return {"status": "active", "mode": "asynchronous"}

# --- JOB MANAGEMENT ENDPOINTS ---

@app.get("/jobs")
def list_jobs():
    """Returns the history of all analysis jobs."""
    return load_all_jobs()

@app.get("/jobs/download-all")
def download_all_results():
    """Generates a ZIP containing all completed analysis plots."""
    jobs = load_all_jobs()
    completed_jobs = [j for j in jobs.values() if j.get("status") == "completed"]
    
    if not completed_jobs:
        raise HTTPException(status_code=400, detail="No hay análisis completos para descargar")

    zip_filename = "VIZO_All_Results.zip"
    zip_path = STORAGE_BASE / zip_filename
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for job in completed_jobs:
            job_id = job["id"]
            metric = job["metric"]
            job_dir = get_job_path(job_id)
            pdf_path = job_dir / f"{metric}.pdf"
            
            if pdf_path.exists():
                zipf.write(pdf_path, arcname=f"{job_id}_{metric}.pdf")
    
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_filename
    )

@app.delete("/jobs/clear-all")
def clear_all_jobs():
    """Deletes all jobs and their files."""
    jobs = load_all_jobs()
    for job in jobs.values():
        delete_job_record(job["id"])
    return {"message": "Todos los trabajos han sido eliminados"}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """Returns the status of a specific job."""
    jobs = load_all_jobs()
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return jobs[job_id]

@app.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    """Deletes a job and its files."""
    delete_job_record(job_id)
    return {"message": f"Trabajo {job_id} eliminado exitosamente"}

@app.get("/jobs/{job_id}/download")
def download_job_results(job_id: str):
    """Generates a ZIP with all original files and the result plot."""
    job_dir = get_job_path(job_id)
    jobs = load_all_jobs()
    
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="El análisis no está listo o falló")

    zip_filename = f"VIZO_Analysis_{job_id}.zip"
    zip_path = job_dir.parent / zip_filename
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in job_dir.iterdir():
            if file.is_file() and not file.name.endswith(".zip"):
                zipf.write(file, arcname=file.name)
    
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_filename
    )

@app.get("/jobs/{job_id}/result")
def get_job_pdf(job_id: str):
    """Returns ONLY the generated PDF for previewing in the frontend."""
    jobs = load_all_jobs()
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="El PDF no está listo")
    
    job_dir = get_job_path(job_id)
    metric = jobs[job_id]["metric"]
    pdf_path = job_dir / f"{metric}.pdf"
    
    if not pdf_path.exists():
        # Fallback if filename is generic
        pdf_path = job_dir / "rmsd.pdf" # checking others if needed
        if not pdf_path.exists():
             raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")

    return FileResponse(path=pdf_path, media_type="application/pdf")


# --- CORE PROCESSING ENDPOINT ---

@app.post("/plot")
async def create_analysis_job(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="No se recibieron archivos.")

    # Tareas de mantenimiento
    cleanup_old_jobs(max_age_hours=2)

    # 1. Agrupar archivos por métrica
    groups = {}
    for upload in files:
        metric = detect_metric(upload.filename)
        if metric not in groups:
            groups[metric] = []
        groups[metric].append(upload)

    jobs_started = []
    
    # 2. Iniciar un Job por cada grupo de métricas
    for metric_name, metric_files in groups.items():
        job_id = str(uuid.uuid4())[:8]
        workspace = get_job_path(job_id)

        saved_paths: List[Path] = []
        for upload in metric_files:
            destination = workspace / upload.filename
            with open(destination, "wb") as f:
                shutil.copyfileobj(upload.file, f)
            saved_paths.append(destination)

        save_job_status(job_id, {
            "id": job_id,
            "status": "running",
            "metric": metric_name,
            "filename_sample": metric_files[0].filename,
            "file_count": len(metric_files)
        })

        # Delegar ejecución al worker
        background_tasks.add_task(run_analysis_task, job_id, metric_name, saved_paths)
        
        jobs_started.append({
            "job_id": job_id, 
            "metric": metric_name
        })

    return {
        "status": "batch_started",
        "jobs": jobs_started,
        "count": len(jobs_started),
        "message": f"Iniciados {len(jobs_started)} análisis independientes."
    }

if __name__ == "__main__":
    import uvicorn
    # En producción (empaquetado), corremos en el puerto 8000 por defecto
    uvicorn.run(app, host="127.0.0.1", port=8000)

