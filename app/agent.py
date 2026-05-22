from .ml_model import CreditRiskModel

ml_model = CreditRiskModel()

def evaluar_cliente(ingreso_anual: float, deuda_pendiente: float, 
                   credit_score: str, pagos_atrasados: int) -> dict:
    """
    Evalúa a un cliente según su ingreso, deuda, score crediticio y pagos atrasados.
    Retorna la decisión del agente experto en formato diccionario.
    """
    ingreso_mensual = ingreso_anual / 12.0

    if ingreso_anual <= 0:
        dti = float('inf')
    else:
        dti = deuda_pendiente / ingreso_anual

    if isinstance(credit_score, str):
       
        if credit_score in ['Good', 'Standard', 'Poor']:
            score_text = credit_score
            
            score_mapping = {'Good': 3, 'Standard': 2, 'Poor': 1}
            num_score = score_mapping[credit_score]
        else:
            try:
                numeric_score = int(credit_score)
                if numeric_score > 700:
                    score_text = 'Good'
                elif numeric_score >= 600:
                    score_text = 'Standard'
                else:
                    score_text = 'Poor'
                num_score = 3 if score_text == 'Good' else (2 if score_text == 'Standard' else 1)
            except:
                
                score_text = 'Standard'
                num_score = 2
    else:
        
        numeric_score = int(credit_score)
        if numeric_score > 700:
            score_text = 'Good'
            num_score = 3
        elif numeric_score >= 600:
            score_text = 'Standard'
            num_score = 2
        else:
            score_text = 'Poor'
            num_score = 1
    
    if dti < 0.1 and score_text == 'Good' and pagos_atrasados <= 1:
        riesgo = "Riesgo Bajo"
        estado = "Aprobado"
        tasa = 15.0
        monto = ingreso_anual * 0.50
    elif dti < 0.3 and num_score >= 2 and pagos_atrasados <= 2:
        riesgo = "Riesgo Medio"
        estado = "Aprobado condicional"
        tasa = 25.0
        monto = ingreso_anual * 0.30
    else:
        riesgo = "Riesgo Alto"
        estado = "Rechazado"
        tasa = 40.0
        monto = ingreso_anual * 0.10

    return {
        "riesgo": riesgo,
        "estado": estado,
        "tasa_interes_anual_pct": tasa,
        "monto_maximo_prestable": round(monto, 2),
        "dti": round(dti, 4)
    }

def determinar_riesgo_reglas(dti, credit_score, pagos_atrasados):
    if dti < 0.1 and credit_score == 'Good' and pagos_atrasados <= 1:
        return "Riesgo Bajo"
    elif dti < 0.3 and credit_score in ['Good', 'Standard'] and pagos_atrasados <= 2:
        return "Riesgo Medio"
    else:
        return "Riesgo Alto"

def asignar_parametros_credito(riesgo, dti, ingreso_anual):
    if riesgo == "Riesgo Bajo":
        estado = "Aprobado"
        tasa = 15.0
        monto = ingreso_anual * 0.50
    elif riesgo == "Riesgo Medio":
        estado = "Aprobado condicional"
        tasa = 25.0
        monto = ingreso_anual * 0.30
    else:
        estado = "Rechazado"
        tasa = 40.0
        monto = ingreso_anual * 0.10
    
    return {
        "riesgo": riesgo,
        "estado": estado,
        "tasa_interes_anual_pct": tasa,
        "monto_maximo_prestable": round(monto, 2),
        "dti": round(dti, 4)
    }