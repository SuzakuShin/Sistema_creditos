def evaluar_cliente(ingreso_anual: float, deuda_pendiente: float, credit_score: str, pagos_atrasados: int) -> dict:
    """
    Evalúa a un cliente según su ingreso, deuda, score crediticio y pagos atrasados.
    Retorna la decisión del agente experto en formato diccionario.
    """
    ingreso_mensual = ingreso_anual / 12.0

    # Calcular relación deuda/ingreso (DTI)
    if ingreso_anual <= 0:
        dti = float('inf')
    else:
        dti = deuda_pendiente / ingreso_anual

    # Mapeo de score textual a numérico (por compatibilidad)
    score_mapping = {'Good': 3, 'Standard': 2, 'Poor': 1}
    num_score = score_mapping.get(credit_score, 2)

    # --------------------------------------
    # Lógica del Sistema Experto de Decisión
    # --------------------------------------
    # Riesgo Bajo:
    #   - DTI < 0.1
    #   - Credit Score > 700
    #   - Pagos atrasados <= 1
    #   → Estado: Aprobado
    #   → Tasa: 15%
    #   → Monto máximo: 50% del ingreso mensual
    #
    # Riesgo Medio:
    #   - 0.1 <= DTI < 0.3
    #   - Credit Score entre 600 y 700
    #   - Pagos atrasados <= 2
    #   → Estado: Aprobado condicional
    #   → Tasa: 25%
    #   → Monto máximo: 30% del ingreso mensual
    #
    # Riesgo Alto:
    #   - DTI >= 0.3
    #   - Credit Score < 600
    #   - Pagos atrasados >= 3
    #   → Estado: Rechazado
    #   → Tasa: 40%
    #   → Monto máximo: 10% del ingreso mensual

    if dti < 0.1 and int(credit_score) > 700 and pagos_atrasados <= 1:
        riesgo = "Riesgo Bajo"
        estado = "Aprobado"
        tasa = 15.0
        monto = ingreso_anual * 0.50
    elif dti < 0.3 and int(credit_score) >= 600 and pagos_atrasados <= 2:
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

