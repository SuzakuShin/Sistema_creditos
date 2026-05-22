#!/bin/bash

echo "========================================="
echo "  CreditRisk Analyzer - Inicio"
echo "========================================="

if ! command -v docker &> /dev/null; then
    echo "Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose no está instalado"
    exit 1
fi

echo " Construyendo imágenes Docker..."
docker-compose build

echo " Iniciando servicios..."
docker-compose up -d

echo ""
echo " Servicios iniciados:"
echo "    API Backend:  http://localhost:8000"
echo "    API Docs:     http://localhost:8000/docs"
echo "    Frontend:     http://localhost:8501"
echo ""
echo "Para detener: docker-compose down"
echo "Para ver logs: docker-compose logs -f"