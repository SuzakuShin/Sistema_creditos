from .tasas_bcra import TasasBCRA


# ============================================================
# SCORECARD DE CRÉDITO - Agente Experto
# ============================================================
# Puntos totales posibles: 100
# Distribución:
#   - DTI Mensual (Cuota estimada/Ingreso): 25 pts
#   - Credit Score (Solvencia histórica):   35 pts
#   - Pagos Atrasados:                      40 pts
#
# Condición de corte:
#   - Más de 5 pagos atrasados = RECHAZO AUTOMÁTICO
#
# Rangos de clasificación final:
#   - Riesgo Bajo   : Score >= 75
#   - Riesgo Medio  : Score >= 45
#   - Riesgo Alto   : Score <  45
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
    cuota_mensual_estimada = deuda_pendiente * 0.025
    return cuota_mensual_estimada / ingreso_mensual


def _calcular_scorecard(dti_mensual: float, score_text: str, pagos_atrasados: int) -> int:
    if pagos_atrasados > 5:
        return 0
    
    puntaje = 0

    if dti_mensual < 0.10:
        puntaje += 25
    elif dti_mensual < 0.20:
        puntaje += 18
    elif dti_mensual < 0.30:
        puntaje += 10
    elif dti_mensual < 0.40:
        puntaje += 4


    if score_text == 'Good':
        puntaje += 35
    elif score_text == 'Standard':
        puntaje += 18

    if pagos_atrasados == 0:
        puntaje += 40
    elif pagos_atrasados == 1:
        puntaje += 25
    elif pagos_atrasados == 2:
        puntaje += 12
    elif pagos_atrasados <= 5:
        puntaje += 3

    return puntaje


def _clasificar_riesgo(puntaje: int) -> tuple[str, str, float]:
    if puntaje >= 75:
        return "Riesgo Bajo", "Aprobado", 0.50
    elif puntaje >= 45:
        return "Riesgo Medio", "Aprobado condicional", 0.30
    else:
        return "Riesgo Alto", "Rechazado", 0.0


def evaluar_cliente(ingreso_anual: float, deuda_pendiente: float,
                    credit_score: str, pagos_atrasados: int) -> dict:
 
    score_text, num_score = _normalizar_score(credit_score)


    dti_mensual = _calcular_dti_mensual(ingreso_anual, deuda_pendiente)

 
    puntaje = _calcular_scorecard(dti_mensual, score_text, pagos_atrasados)


    riesgo, estado, factor_monto = _clasificar_riesgo(puntaje)
    monto = round(ingreso_anual * factor_monto, 2)

    tasa = 0.0
    fundamentacion_tasa = None
    
    if riesgo != "Riesgo Alto": 
        try:
            bcra = TasasBCRA()
            resultado_tasa = bcra.calcular_tasa_final(
                riesgo, dti_mensual, score_text, pagos_atrasados
            )
            tasa = resultado_tasa["tasa_nominal_anual"]
            fundamentacion_tasa = resultado_tasa["fundamentacion"]
        except Exception as e:
            print(f"⚠️ Error obteniendo tasa BCRA: {e}")
            # Fallback a tasas fijas
            tasas_fallback = {"Riesgo Bajo": 65.0, "Riesgo Medio": 100.0}
            tasa = tasas_fallback.get(riesgo, 0.0)

    return {
        "riesgo": riesgo,
        "estado": estado,
        "tasa_interes_anual_pct": round(tasa, 2),
        "monto_maximo_prestable": monto,
        "dti": round(dti_mensual, 4),
        "score_crediticio": puntaje,
        "fundamentacion_tasa": fundamentacion_tasa
    }

def determinar_riesgo_reglas(dti, credit_score, pagos_atrasados):
    score_text, _ = _normalizar_score(credit_score)
    puntaje = _calcular_scorecard(dti, score_text, pagos_atrasados)
    riesgo, _, _ = _clasificar_riesgo(puntaje)
    return riesgo


def asignar_parametros_credito(riesgo, dti, ingreso_anual):
    if riesgo == "Riesgo Bajo":
        estado, monto = "Aprobado", ingreso_anual * 0.50
    elif riesgo == "Riesgo Medio":
        estado, monto = "Aprobado condicional", ingreso_anual * 0.30
    else:
        estado, monto = "Rechazado", 0.0

    return {
        "riesgo": riesgo,
        "estado": estado,
        "tasa_interes_anual_pct": 0.0,
        "monto_maximo_prestable": round(monto, 2),
        "dti": round(dti, 4)
    }