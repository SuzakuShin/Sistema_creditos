@echo off
title CreditRisk Analyzer - Inicio

echo.
echo Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado
    echo Instala Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)

echo Verificando dependencias...
if not exist "node_modules\cli-progress" (
    echo Instalando dependencias...
    npm install
)

echo.
node start.js
pause