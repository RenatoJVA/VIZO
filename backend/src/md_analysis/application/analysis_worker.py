from pathlib import Path
from typing import List
import traceback
from ..infrastructure.persistence.local_storage import save_job_status
from ..infrastructure.plotting.metrics import METRIC_MAP

def run_analysis_task(job_id: str, metric_name: str, input_files: List[Path]):
    """
    Background worker that performs the plotting and updates the job status.
    This runs independently of the main API response.
    """
    try:
        plotter = METRIC_MAP[metric_name]
        output_pdf = input_files[0].parent / f"{metric_name}.pdf"
        
        # 1. Start processing
        plotter.plot(input_files, output_pdf)
        
        # 2. Mark as completed
        save_job_status(job_id, {
            "id": job_id,
            "status": "completed",
            "metric": metric_name,
            "result_file": output_pdf.name,
            "file_count": len(input_files)
        })
        
    except Exception as e:
        # 3. Handle errors in background
        trace = traceback.format_exc()
        print(f"--- ERROR EN JOB {job_id} ---")
        print(trace)
        print("----------------------------")
        
        save_job_status(job_id, {
            "id": job_id,
            "status": "failed",
            "metric": metric_name,
            "error": f"{type(e).__name__}: {str(e)}"
        })
