from pydantic import BaseModel, Field, validator
from typing import Union

class ClienteEval(BaseModel):
    Annual_Income: float = Field(..., description="Ingreso anual del cliente en dólares", gt=0)
    Outstanding_Debt: float = Field(..., description="Deuda pendiente del cliente", ge=0)
    Credit_Score: str = Field(..., description="Score crediticio histórico (Good, Standard, Poor o valor numérico)")
    Pagos_Atrasados: int = Field(..., description="Cantidad de pagos atrasados registrados", ge=0)
    
    @validator('Credit_Score')
    def validar_credit_score(cls, v):
       
        if v in ['Good', 'Standard', 'Poor']:
            return v
        
        # Aceptar valores numéricos como string
        try:
            score_num = int(v)
            if 300 <= score_num <= 850:
                return v
            else:
                raise ValueError('Credit_Score numérico debe estar entre 300 y 850')
        except ValueError:
            raise ValueError('Credit_Score debe ser Good, Standard, Poor o un número entre 300-850')
    
    @validator('Annual_Income')
    def validar_ingreso(cls, v):
        if v <= 0:
            raise ValueError('El ingreso anual debe ser mayor que 0')
        if v > 10000000:  
            raise ValueError('El ingreso anual parece demasiado alto')
        return v
    
    @validator('Outstanding_Debt')
    def validar_deuda(cls, v):
        if v < 0:
            raise ValueError('La deuda pendiente no puede ser negativa')
        return v

class DecisionResponse(BaseModel):
    riesgo: str = Field(..., description="Nivel de riesgo determinado (Riesgo Bajo, Medio o Alto)")
    estado: str = Field(..., description="Decisión final (Aprobado, Aprobado condicional, Rechazado)")
    tasa_interes_anual_pct: float = Field(..., description="Tasa de interés anual asignada en %")
    monto_maximo_prestable: float = Field(..., description="Monto máximo que se le puede prestar")
    dti: float = Field(..., description="Relación Deuda/Ingreso calculada")