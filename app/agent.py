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
    """Convierte el Credit Score a texto estandarizado y puntaje numérico (1-3)."""
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
    """
    Calcula el DTI mensual (estándar bancario).
    Se estima la cuota mensual como el 2.5% de la deuda total pendiente,
    y se compara contra el ingreso mensual bruto.
    """
    if ingreso_anual <= 0:
        return float('inf')
    ingreso_mensual = ingreso_anual / 12.0
    # Estimación de cuota mensual: 2.5% de la deuda total
    cuota_mensual_estimada = deuda_pendiente * 0.025
    return cuota_mensual_estimada / ingreso_mensual


def _calcular_scorecard(dti_mensual: float, score_text: str, pagos_atrasados: int) -> int:
    """
    Scorecard de crédito (0–100 puntos).
    Devuelve el puntaje total.
    """
    puntaje = 0

    # --- DTI Mensual (30 pts) ---
    if dti_mensual < 0.10:
        puntaje += 30   # Excelente: cuota < 10% del ingreso mensual
    elif dti_mensual < 0.20:
        puntaje += 22   # Bueno: 10–20%
    elif dti_mensual < 0.30:
        puntaje += 14   # Precaución: 20–30%
    elif dti_mensual < 0.40:
        puntaje += 6    # Riesgo: 30–40%
    else:
        puntaje += 0    # Crítico: > 40%

    # --- Credit Score / Solvencia (50 pts) ---
    if score_text == 'Good':
        puntaje += 50
    elif score_text == 'Standard':
        puntaje += 28
    else:  # Poor
        puntaje += 0

    # --- Pagos Atrasados (20 pts) ---
    if pagos_atrasados == 0:
        puntaje += 20   # Sin atrasos: perfecto
    elif pagos_atrasados <= 1:
        puntaje += 14   # 1 atraso: aceptable
    elif pagos_atrasados <= 3:
        puntaje += 6    # 2–3 atrasos: precaución
    else:
        puntaje += 0    # Más de 3 atrasos: señal de alerta

    return puntaje


def _clasificar_riesgo(puntaje: int) -> tuple[str, str, float, float]:
    """
    Clasifica el riesgo y asigna parámetros de crédito según el puntaje.
    Retorna: (riesgo, estado, tasa, factor_monto)
    """
    if puntaje >= 70:
        return "Riesgo Bajo", "Aprobado", 15.0, 0.50
    elif puntaje >= 40:
        return "Riesgo Medio", "Aprobado condicional", 25.0, 0.30
    else:
        return "Riesgo Alto", "Rechazado", 0.0, 0.0


def evaluar_cliente(ingreso_anual: float, deuda_pendiente: float,
                    credit_score: str, pagos_atrasados: int) -> dict:
    """
    Función principal del Agente Experto de Scoring Crediticio.

    Flujo:
    1. Normalización del Credit Score
    2. Cálculo del DTI mensual (estándar bancario)
    3. Scorecard de puntos (0–100)
    4. Clasificación en Riesgo Bajo / Medio / Alto
    5. Asignación de tasa de interés y monto máximo prestable
    """
    # 1. Normalizar Credit Score
    score_text, num_score = _normalizar_score(credit_score)

    # 2. DTI mensual bancario
    dti_mensual = _calcular_dti_mensual(ingreso_anual, deuda_pendiente)

    # 3. Scorecard
    puntaje = _calcular_scorecard(dti_mensual, score_text, pagos_atrasados)

    # 4. Clasificación y parámetros de crédito
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


# ============================================================
# Funciones auxiliares mantenidas para compatibilidad con API
# ============================================================

def determinar_riesgo_reglas(dti, credit_score, pagos_atrasados):
    """Compatibilidad: determina riesgo usando el scorecard."""
    score_text, _ = _normalizar_score(credit_score)
    puntaje = _calcular_scorecard(dti, score_text, pagos_atrasados)
    riesgo, _, _, _ = _clasificar_riesgo(puntaje)
    return riesgo


def asignar_parametros_credito(riesgo, dti, ingreso_anual):
    """Compatibilidad: asigna parámetros de crédito según nivel de riesgo."""
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