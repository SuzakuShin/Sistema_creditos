@echo off
echo =========================================
echo   CreditRisk Analyzer - Inicio
echo =========================================
echo.

echo Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Docker no esta instalado
    pause
    exit /b 1
)

echo  Construyendo imagenes Docker...
docker-compose build

echo.
echo  Iniciando servicios...
docker-compose up -d

echo.
echo  Servicios iniciados:
echo     API Backend:  http://localhost:8000
echo     API Docs:     http://localhost:8000/docs
echo     Frontend:     http://localhost:8501
echo.
echo "Para detener: docker-compose down"
echo "Para ver logs: docker-compose logs -f"
echo.
pause