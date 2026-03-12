#!/bin/bash

echo "=========================================="
echo "    VIZO - PROCESO DE BUILD AUTOMATICO"
echo "=========================================="

# 1. Frontend
echo ""
echo "[1/3] Construyendo Frontend (Vue)..."
cd frontend
bun run build
if [ $? -ne 0 ]; then
    echo "[ERROR] Falló la construcción del frontend."
    exit 1
fi
cd ..

# 2. Backend
echo ""
echo "[2/3] Construyendo Backend (Python/FastAPI)..."
cd backend
uv run pyinstaller vizo-backend.spec
if [ $? -ne 0 ]; then
    echo "[ERROR] Falló la construcción del backend."
    exit 1
fi
cd ..

# 3. Electron
echo ""
echo "[3/3] Creando instalador final..."
bun run dist
if [ $? -ne 0 ]; then
    echo "[ERROR] Falló el empaquetado final de Electron."
    exit 1
fi

echo ""
echo "=========================================="
echo "    BUILD COMPLETADO EXITOSAMENTE"
echo "=========================================="
echo "El instalador se encuentra en la carpeta: release"
echo ""
