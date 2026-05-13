from pydantic import BaseModel, Field

class ClienteEval(BaseModel):
    Annual_Income: float = Field(..., description="Ingreso anual del cliente en dólares")
    Outstanding_Debt: float = Field(..., description="Deuda pendiente del cliente")
    Credit_Score: str = Field(..., description="Score crediticio histórico (Good, Standard, Poor o valor numérico)")
    Pagos_Atrasados: int = Field(..., description="Cantidad de pagos atrasados registrados")

class DecisionResponse(BaseModel):
    riesgo: str = Field(..., description="Nivel de riesgo determinado (Riesgo Bajo, Medio o Alto)")
    estado: str = Field(..., description="Decisión final (Aprobado, Aprobado condicional, Rechazado)")
    tasa_interes_anual_pct: float = Field(..., description="Tasa de interés anual asignada en %")
    monto_maximo_prestable: float = Field(..., description="Monto máximo que se le puede prestar")
    dti: float = Field(..., description="Relación Deuda/Ingreso calculada")

