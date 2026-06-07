from .ml_model import CreditRiskModel

ml_model = CreditRiskModel()

# ============================================================
# SCORECARD DE CRÉDITO - Agente Experto
# ============================================================
# Puntos totales posibles: 100
# Distribución:
#   - DTI Mensual (Deuda/Ingreso):  30 pts
#   - Credit Score (Solvencia):     50 pts
#   - Pagos Atrasados:              20 pts
#
# Rangos de clasificación final:
#   - Riesgo Bajo   : Score >= 70
#   - Riesgo Medio  : Score >= 40
#   - Riesgo Alto   : Score <  40
# ============================================================

def _normalizar_score(credit_score) -> tuple[str, int]:
    if isinstance(credit_score, str):
        if credit_score in ['Good', 'Standard', 'Poor']:
            score_text = credit_score
        else:
            try:
                numeric_score = int(credit_score)
                if numeric_score > 700:
                    score_text = 'Good'
                elif numeric_score >= 600:
                    score_text = 'Standard'
                else:
                    score_text = 'Poor'
            except (ValueError, TypeError):
                score_text = 'Standard'
    else:
        try:
            numeric_score = int(credit_score)
            if numeric_score > 700:
                score_text = 'Good'
            elif numeric_score >= 600:
                score_text = 'Standard'
            else:
                score_text = 'Poor'
        except (ValueError, TypeError):
            score_text = 'Standard'

    num_score = {'Good': 3, 'Standard': 2, 'Poor': 1}[score_text]
    return score_text, num_score


def _calcular_dti_mensual(ingreso_anual: float, deuda_pendiente: float) -> float:
    if ingreso_anual <= 0:
        return float('inf')
    ingreso_mensual = ingreso_anual / 12.0
    # Estimación de cuota mensual: 2.5% de la deuda total
    cuota_mensual_estimada = deuda_pendiente * 0.025
    return cuota_mensual_estimada / ingreso_mensual


def _calcular_scorecard(dti_mensual: float, score_text: str, pagos_atrasados: int) -> int:
    puntaje = 0
    if dti_mensual < 0.10:
        puntaje += 30 
    elif dti_mensual < 0.20:
        puntaje += 22   
    elif dti_mensual < 0.30:
        puntaje += 14 
    elif dti_mensual < 0.40:
        puntaje += 6   
    else:
        puntaje += 0  
    if score_text == 'Good':
        puntaje += 50
    elif score_text == 'Standard':
        puntaje += 28
    else:
        puntaje += 0

    if pagos_atrasados == 0:
        puntaje += 20 
    elif pagos_atrasados <= 1:
        puntaje += 14  
    elif pagos_atrasados <= 3:
        puntaje += 6   
    else:
        puntaje += 0  

    return puntaje


def _clasificar_riesgo(puntaje: int) -> tuple[str, str, float, float]:
    if puntaje >= 70:
        return "Riesgo Bajo", "Aprobado", 15.0, 0.50
    elif puntaje >= 40:
        return "Riesgo Medio", "Aprobado condicional", 25.0, 0.30
    else:
        return "Riesgo Alto", "Rechazado", 0.0, 0.0


def evaluar_cliente(ingreso_anual: float, deuda_pendiente: float,
                    credit_score: str, pagos_atrasados: int) -> dict:
    score_text, num_score = _normalizar_score(credit_score)
    dti_mensual = _calcular_dti_mensual(ingreso_anual, deuda_pendiente)
    puntaje = _calcular_scorecard(dti_mensual, score_text, pagos_atrasados)
    riesgo, estado, tasa, factor_monto = _clasificar_riesgo(puntaje)
    monto = round(ingreso_anual * factor_monto, 2)

    return {
        "riesgo": riesgo,
        "estado": estado,
        "tasa_interes_anual_pct": tasa,
        "monto_maximo_prestable": monto,
        "dti": round(dti_mensual, 4),
        "score_crediticio": puntaje
    }

def determinar_riesgo_reglas(dti, credit_score, pagos_atrasados):
    score_text, _ = _normalizar_score(credit_score)
    puntaje = _calcular_scorecard(dti, score_text, pagos_atrasados)
    riesgo, _, _, _ = _clasificar_riesgo(puntaje)
    return riesgo


def asignar_parametros_credito(riesgo, dti, ingreso_anual):
    if riesgo == "Riesgo Bajo":
        estado, tasa, monto = "Aprobado", 15.0, ingreso_anual * 0.50
    elif riesgo == "Riesgo Medio":
        estado, tasa, monto = "Aprobado condicional", 25.0, ingreso_anual * 0.30
    else:
        estado, tasa, monto = "Rechazado", 0.0, 0.0

    return {
        "riesgo": riesgo,
        "estado": estado,
        "tasa_interes_anual_pct": tasa,
        "monto_maximo_prestable": round(monto, 2),
        "dti": round(dti, 4)
    }