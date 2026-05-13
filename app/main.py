import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from .schemas import ClienteEval, DecisionResponse
from .agent import evaluar_cliente

# Variables globales para cachear los datos en memoria
df_limpio = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df_limpio
    # Carga de datos limpios al inicio
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'clientes_limpios.csv')
    try:
        df_limpio = pd.read_csv(data_path, low_memory=False)
        print(f"Dataset cargado en memoria exitosamente: {len(df_limpio)} registros.")
    except Exception as e:
        print(f"Advertencia: No se pudo cargar el dataset limpio. ¿Ejecutaste data_cleaner.py? Detalle: {e}")
        df_limpio = pd.DataFrame()
    yield
    # Limpieza al apagar si fuera necesario
    df_limpio = None


app = FastAPI(
    title="Sistema Experto de Scoring Crediticio",
    description="API para evaluar riesgo crediticio mediante un agente de decisión.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", tags=["Salud del Sistema"])
def health_check():
    """
    Endpoint para verificar que el sistema esté funcionando correctamente.
    """
    return {
        "status": "ok",
        "dataset_cargado": df_limpio is not None and not df_limpio.empty,
        "registros_disponibles": len(df_limpio) if df_limpio is not None else 0
    }


@app.post("/evaluar", response_model=DecisionResponse, tags=["Evaluación Crediticia"])
def evaluar(cliente: ClienteEval):
    """
    Evalúa el perfil de un solicitante usando el agente experto y devuelve la decisión tomada.
    """
    decision = evaluar_cliente(
        ingreso_anual=cliente.Annual_Income,
        deuda_pendiente=cliente.Outstanding_Debt,
        credit_score=cliente.Credit_Score,
        pagos_atrasados=cliente.Pagos_Atrasados   # 🔹 este campo faltaba
    )
    return decision



@app.get("/cliente/{cliente_id}", tags=["Consultas de Clientes"])
def obtener_cliente(cliente_id: str):
    """
    Busca los datos de un cliente específico (ej. CUS_0xd40) en el dataset limpio y muestra su decisión de crédito pre-calculada.
    """
    if df_limpio is None or df_limpio.empty:
        raise HTTPException(status_code=503, detail="El dataset no está disponible")
    
    # Filtrar cliente (en el CSV se llama Customer_ID)
    cliente = df_limpio[df_limpio['Customer_ID'] == cliente_id]
    
    if cliente.empty:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Usar el primer registro del cliente (podría haber varios meses, tomamos el más reciente o el primero)
    datos_cliente = cliente.iloc[0]
    
    # Evaluamos con nuestro agente
    decision = evaluar_cliente(
        ingreso_anual=datos_cliente['Annual_Income'],
        deuda_pendiente=datos_cliente['Outstanding_Debt'],
        credit_score=datos_cliente['Credit_Score']
    )
    
    return {
        "Customer_ID": cliente_id,
        "datos_base": {
            "ingreso_anual": datos_cliente['Annual_Income'],
            "deuda_pendiente": datos_cliente['Outstanding_Debt'],
            "score": datos_cliente['Credit_Score']
        },
        "decision_agente": decision
    }


@app.get("/estadisticas", tags=["Estadísticas Globales"])
def obtener_estadisticas():
    """
    Retorna métricas globales del dataset de clientes limpios.
    """
    if df_limpio is None or df_limpio.empty:
        raise HTTPException(status_code=503, detail="El dataset no está disponible")
    
    avg_income = df_limpio['Annual_Income'].mean()
    avg_debt = df_limpio['Outstanding_Debt'].mean()
    
    # Distribución de credit score
    score_counts = df_limpio['Credit_Score'].value_counts().to_dict()
    
    return {
        "total_registros": len(df_limpio),
        "ingreso_anual_promedio": round(avg_income, 2),
        "deuda_pendiente_promedio": round(avg_debt, 2),
        "distribucion_scores": score_counts,
        "dti_promedio": round(avg_debt / avg_income if avg_income else 0, 4)
    }

