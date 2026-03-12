import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

def get_storage_path() -> Path:
    """Returns the base path for storage, adapting to production/desktop environments."""
    if getattr(sys, 'frozen', False):
        # Si la app está empaquetada (.exe), usamos AppData/Local/VIZO
        if os.name == 'nt':
            base = Path(os.environ.get('LOCALAPPDATA', Path.home())) / "VIZO"
        else:
            base = Path.home() / ".vizo"
    else:
        # En desarrollo, seguimos usando la carpeta local 'storage'
        base = Path("storage")
    
    base.mkdir(parents=True, exist_ok=True)
    return base

STORAGE_BASE = get_storage_path()
JOBS_INDEX = STORAGE_BASE / "jobs_registry.json"

def init_storage():
    """Ensures storage directory and index exist."""
    if not JOBS_INDEX.exists():
        with open(JOBS_INDEX, "w") as f:
            json.dump({}, f)

def save_job_status(job_id: str, status_data: Dict[str, Any]):
    """Saves or updates job metadata in the JSON registry."""
    init_storage()
    registry = load_all_jobs()
    
    # Update timestamp
    status_data["updated_at"] = datetime.now().isoformat()
    if "created_at" not in status_data:
        status_data["created_at"] = status_data["updated_at"]
        
    registry[job_id] = status_data
    with open(JOBS_INDEX, "w") as f:
        json.dump(registry, f, indent=4)

def load_all_jobs() -> Dict[str, Any]:
    """Loads all job records from the local registry."""
    if not JOBS_INDEX.exists():
        return {}
    with open(JOBS_INDEX, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def get_job_path(job_id: str) -> Path:
    """Returns the dedicated directory path for a specific job."""
    path = STORAGE_BASE / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path

def delete_job_record(job_id: str):
    """Removes a job from registry and deletes its files."""
    registry = load_all_jobs()
    if job_id in registry:
        del registry[job_id]
        with open(JOBS_INDEX, "w") as f:
            json.dump(registry, f, indent=4)
    
    import shutil
    job_dir = STORAGE_BASE / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
        # Also delete associated zip if exists
        zip_path = STORAGE_BASE / f"VIZO_Analysis_{job_id}.zip"
        if zip_path.exists():
            zip_path.unlink()

def cleanup_old_jobs(max_age_hours: int = 2):
    """Deletes jobs and files older than the specified hours."""
    registry = load_all_jobs()
    now = datetime.now()
    to_delete = []
    
    for job_id, data in registry.items():
        try:
            created_at = datetime.fromisoformat(data.get("created_at", data.get("updated_at")))
            age = now - created_at
            if age.total_seconds() > (max_age_hours * 3600):
                to_delete.append(job_id)
        except Exception:
            to_delete.append(job_id) # Delete if date is corrupt
            
    for job_id in to_delete:
        print(f"Cleaning up old job: {job_id}")
        delete_job_record(job_id)
