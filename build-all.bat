@echo off
setlocal

echo ==========================================
echo    VIZO - PROCESO DE BUILD AUTOMATICO
echo ==========================================

:: 1. Frontend
echo.
echo [1/3] Construyendo Frontend (Vue)...
cd frontend
call bun run build
if %errorlevel% neq 0 (
    echo [ERROR] Falló la construcción del frontend.
    pause
    exit /b %errorlevel%
)
cd ..

:: 2. Backend
echo.
echo [2/3] Construyendo Backend (Python/FastAPI)...
cd backend
call uv run pyinstaller vizo-backend.spec
if %errorlevel% neq 0 (
    echo [ERROR] Falló la construcción del backend.
    pause
    exit /b %errorlevel%
)
cd ..

:: 3. Electron
echo.
echo [3/3] Creando instalador final (.exe)...
call bun run dist
if %errorlevel% neq 0 (
    echo [ERROR] Falló el empaquetado final de Electron.
    pause
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo    BUILD COMPLETADO EXITOSAMENTE
echo ==========================================
echo El instalador se encuentra en la carpeta: release
echo.
pause
