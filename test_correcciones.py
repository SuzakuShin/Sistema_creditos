# test_correcciones.py
"""
Script para verificar que los bugs han sido corregidos
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.agent import evaluar_cliente

def test_credit_score_texto():
    """Test #1: Verificar que acepta credit_score como texto"""
    print("Test 1: Credit Score como texto...")
    try:
        result = evaluar_cliente(
            ingreso_anual=60000,
            deuda_pendiente=5000,
            credit_score="Good",  # Texto
            pagos_atrasados=0
        )
        assert result['riesgo'] == "Riesgo Bajo", f"Esperado: Riesgo Bajo, Obtenido: {result['riesgo']}"
        print("✅ PASS: Maneja correctamente credit_score como texto")
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")

def test_credit_score_numerico():
    """Test #2: Verificar que acepta credit_score numérico"""
    print("\nTest 2: Credit Score numérico...")
    try:
        result = evaluar_cliente(
            ingreso_anual=60000,
            deuda_pendiente=5000,
            credit_score="750",  # Número como string
            pagos_atrasados=0
        )
        assert result['riesgo'] == "Riesgo Bajo", f"Esperado: Riesgo Bajo, Obtenido: {result['riesgo']}"
        print("✅ PASS: Maneja correctamente credit_score numérico")
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")

def test_dti_alto():
    """Test #3: Verificar clasificación de alto riesgo"""
    print("\nTest 3: Cliente de alto riesgo...")
    result = evaluar_cliente(
        ingreso_anual=30000,
        deuda_pendiente=25000,  # DTI alto
        credit_score="Poor",
        pagos_atrasados=5
    )
    assert result['riesgo'] == "Riesgo Alto", f"Esperado: Riesgo Alto, Obtenido: {result['riesgo']}"
    print(f"✅ PASS: Clasifica correctamente como {result['riesgo']}")

def test_todos_los_parametros():
    """Test #4: Verificar que todos los parámetros son aceptados"""
    print("\nTest 4: Validación de parámetros...")
    result = evaluar_cliente(
        ingreso_anual=50000,
        deuda_pendiente=10000,
        credit_score="Standard",
        pagos_atrasados=1
    )
    campos_requeridos = ['riesgo', 'estado', 'tasa_interes_anual_pct', 'monto_maximo_prestable', 'dti']
    for campo in campos_requeridos:
        assert campo in result, f"Falta el campo {campo}"
    print("✅ PASS: Todos los campos están presentes en la respuesta")

if __name__ == "__main__":
    print("🔍 Iniciando pruebas de corrección de bugs...\n")
    
    test_credit_score_texto()
    test_credit_score_numerico()
    test_dti_alto()
    test_todos_los_parametros()
    
    print("\n✨ Todas las pruebas completadas!")