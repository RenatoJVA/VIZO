# import os
# from src.rmsd import plot_rmsd
# from src.rmsf import plot_rmsf
# from src.rg import plot_rg
# from src.sasa import plot_sasa
# from src.hbnum import plot_hbnum

# PLOTS = {
#     "rmsd": (plot_rmsd, "rmsd_clasico.pdf"),
#     "rmsf": (plot_rmsf, "rmsf_clasico.pdf"),
#     "rg": (plot_rg, "rg.pdf"),
#     "sasa": (plot_sasa, "sasa.pdf"),
#     "hbnum": (plot_hbnum, "hbnum.pdf"),
# }


# def get_available_files(metric):
#     return sorted(f for f in os.listdir("XVG") if f.endswith(f"-{metric}.xvg"))


# def select_files(metric):
#     files = get_available_files(metric)
#     if not files:
#         print(f"No {metric.upper()} files found in XVG/")
#         return []

#     print(f"\nAvailable {metric.upper()} files:")
#     for i, f in enumerate(files, 1):
#         print(f"  {i}. {f}")

#     sel = input("\nSelect files (numbers or 'all'): ").strip()
#     if sel.lower() == "all":
#         return [os.path.join("XVG", f) for f in files]

#     try:
#         idx = [int(x) - 1 for x in sel.split(",")]
#         return [os.path.join("XVG", files[i]) for i in idx if 0 <= i < len(files)]
#     except:
#         print("Invalid selection.")
#         return select_files(metric)


# def get_corresponding_files(files, metric):
#     metrics = ("rmsd", "rmsf", "rg", "sasa", "hbnum")
#     return [
#         f"{os.path.join(*file.split(os.sep)[:-1])}/{os.path.basename(file).replace(tuple(f'-{m}.xvg' for m in metrics), '')}-{metric}.xvg"
#         if False
#         else file.replace(
#             next(f"-{m}.xvg" for m in metrics if file.endswith(f"-{m}.xvg")),
#             f"-{metric}.xvg",
#         )
#         for file in files
#     ]


# def main():
#     print("=== MD Analysis Comparison Tool ===\n")

#     rmsd_files = select_files("rmsd")
#     if not rmsd_files:
#         return

#     func, out = PLOTS["rmsd"]
#     print("\nGenerating RMSD comparison plot...")
#     func(rmsd_files, out)

#     metrics = ["rmsf", "rg", "sasa", "hbnum"]

#     if len(rmsd_files) > 1:
#         for m in metrics:
#             func, out = PLOTS[m]
#             print(f"Generating {m.upper()} plot...")
#             func(get_corresponding_files(rmsd_files, m), out)
#         print("\nAll plots generated successfully.")
#     else:
#         for m in metrics:
#             files = select_files(m)
#             if files:
#                 func, out = PLOTS[m]
#                 print(f"\nGenerating {m.upper()} plot...")
#                 func(files, out)


# if __name__ == "__main__":
#     main()
"""
MD Analysis Backend — FastAPI
==============================
Endpoints:
  POST /plot   →  recibe archivos XVG, genera un PDF y lo devuelve
  GET  /health →  verifica que el servidor está vivo

Cómo correr:
  uvicorn main:app --reload --port 8000
"""

import os
import shutil
import tempfile
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Importamos las funciones que ya tienes — no se tocan
from services.rmsd import plot_rmsd
from services.rmsf import plot_rmsf
from services.rg import plot_rg
from services.sasa import plot_sasa
from services.hbnum import plot_hbnum

# ─────────────────────────────────────────────────────────────────
# 1. CREAR LA APP
#    FastAPI() crea el servidor. El título aparece en la doc
#    automática que FastAPI genera en http://localhost:8000/docs
# ─────────────────────────────────────────────────────────────────
app = FastAPI(title="MD Analysis API", version="1.0.0")


# ─────────────────────────────────────────────────────────────────
# 2. CORS (Cross-Origin Resource Sharing)
#
#    El navegador bloquea peticiones entre dominios/puertos distintos
#    por seguridad. Vue corre en :5173 y FastAPI en :8000 → puertos
#    distintos → el navegador bloquea.
#
#    CORSMiddleware le dice a FastAPI que responda con los headers
#    HTTP que le indican al navegador "está bien, deja pasar".
# ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],  # GET, POST, etc.
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────
# 3. MAPA MÉTRICA → FUNCIÓN
#
#    Diccionario que relaciona el sufijo del archivo con su función.
#    Para agregar PCA, Heatmap, etc. solo añades la entrada aquí
#    y el import correspondiente arriba.
# ─────────────────────────────────────────────────────────────────
PLOT_FUNCTIONS = {
    "rmsd": plot_rmsd,
    "rmsf": plot_rmsf,
    "rg": plot_rg,
    "sasa": plot_sasa,
    "hbnum": plot_hbnum,
}


# ─────────────────────────────────────────────────────────────────
# 4. FUNCIÓN AUXILIAR: detectar métrica desde el nombre
#
#    "proteina-rmsd.xvg"  →  "rmsd"
#    "wt-sasa.xvg"        →  "sasa"
#
#    Si el nombre no coincide con ninguna métrica conocida,
#    lanzamos un HTTPException con código 400 (Bad Request).
#    FastAPI convierte esto automáticamente en JSON:
#      { "detail": "No se pudo detectar..." }
# ─────────────────────────────────────────────────────────────────
def detect_metric(filename: str) -> str:
    for metric in PLOT_FUNCTIONS:
        if filename.endswith(f"-{metric}.xvg"):
            return metric
    raise HTTPException(
        status_code=400,
        detail=(
            f"No se pudo detectar la métrica del archivo '{filename}'. "
            f"El nombre debe terminar en: "
            + ", ".join(f"-{m}.xvg" for m in PLOT_FUNCTIONS)
        ),
    )


# ─────────────────────────────────────────────────────────────────
# 5. ENDPOINT: GET /health
#
#    Endpoint simple para verificar que el servidor está vivo.
#    Útil para debugging: abre http://localhost:8000/health
# ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "metrics_available": list(PLOT_FUNCTIONS.keys())}


# ─────────────────────────────────────────────────────────────────
# 6. ENDPOINT PRINCIPAL: POST /plot
#
#    @app.post("/plot") le dice a FastAPI:
#      "cuando llegue una petición POST a la ruta /plot,
#       ejecuta esta función y devuelve su resultado"
#
#    `async def` — función asíncrona. Permite que FastAPI
#    atienda otras peticiones mientras espera operaciones lentas
#    (leer disco, etc.). Es la forma estándar en FastAPI.
#
#    `files: List[UploadFile] = File(...)`
#      FastAPI lee el multipart/form-data y convierte cada archivo
#      en un objeto UploadFile con atributos:
#        .filename  → nombre original del archivo
#        .file      → objeto tipo-archivo para leer el contenido
# ─────────────────────────────────────────────────────────────────
@app.post("/plot")
async def generate_plot(files: List[UploadFile] = File(...)):

    if not files:
        raise HTTPException(status_code=400, detail="No se recibieron archivos.")

    # tempfile.mkdtemp() crea una carpeta temporal única en /tmp/
    # Usamos carpeta temporal para no ensuciar el proyecto con archivos
    # de usuarios distintos mezclados.
    tmp_dir = tempfile.mkdtemp()

    try:
        # ── Paso 1: guardar archivos en disco ──────────────────────
        # UploadFile viene del HTTP request — está en memoria/red.
        # Necesitamos escribirlo en disco para que matplotlib lo lea.
        # shutil.copyfileobj copia de un objeto-archivo a otro
        # eficientemente (en chunks), sin cargar todo en RAM.
        saved_paths: List[str] = []
        for upload in files:
            destination = os.path.join(tmp_dir, upload.filename)
            with open(destination, "wb") as f:
                shutil.copyfileobj(upload.file, f)
            saved_paths.append(destination)

        # ── Paso 2: detectar métrica ───────────────────────────────
        # Usamos un set (conjunto) para detectar métricas únicas.
        # Si el usuario sube rmsd + sasa juntos → error claro.
        metrics_found = {detect_metric(os.path.basename(p)) for p in saved_paths}

        if len(metrics_found) > 1:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Todos los archivos deben ser de la misma métrica. "
                    f"Se detectaron: {metrics_found}"
                ),
            )

        metric = metrics_found.pop()  # extrae el único elemento del set

        # ── Paso 3: generar el PDF ─────────────────────────────────
        # Ruta de salida en la carpeta temporal
        output_pdf = os.path.join(tmp_dir, f"{metric}.pdf")

        # Obtenemos la función correcta del diccionario y la llamamos
        # exactamente igual que en tu main.py original:
        #   plot_rmsd(["path/a.xvg", "path/b.xvg"], "salida.pdf")
        plot_fn = PLOT_FUNCTIONS[metric]
        plot_fn(saved_paths, output_pdf)

        # ── Paso 4: devolver el PDF al navegador ───────────────────
        # FileResponse lee el archivo y lo envía como respuesta HTTP
        # con el Content-Type correcto (application/pdf).
        # El navegador lo recibe como un blob binario.
        return FileResponse(
            path=output_pdf,
            media_type="application/pdf",
            filename=f"{metric}.pdf",  # nombre sugerido para descarga
        )

    except HTTPException:
        # Re-lanzamos los HTTPException que creamos nosotros (400, etc.)
        # antes de limpiar, para que FastAPI los maneje correctamente
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    except Exception as e:
        # Cualquier error inesperado: matplotlib, numpy, archivo corrupto
        # Lo convertimos en un 500 con el mensaje para facilitar debugging
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
