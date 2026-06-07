# app/tasas_bcra.py
import requests
from datetime import datetime

# Tu token de estadisticasbcra.com
BCRA_TOKEN = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MTIwNjk0MTcsInR5cGUiOiJleHRlcm5hbCIsInVzZXIiOiJzdXpha3Uuc2hpbi5hZ0BnbWFpbC5jb20ifQ.LiXa54B1iMuJz7UikxiLZW7K9h0A2gSTlxWRi0_J6Utb82faqFxfjddj0oBhjYGLTx9r1_tdTK14PByrIum3FA"

class TasasBCRA:
    """
    Cliente para la API de estadisticasbcra.com
    Documentación: https://estadisticasbcra.com/api/documentacion
    """
    
    def __init__(self):
        self.base_url = "https://api.estadisticasbcra.com"
        self.headers = {"Authorization": f"BEARER {BCRA_TOKEN}"}
    
    def _get(self, endpoint):
        """Realiza una consulta GET a la API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return data[-1]  # Último dato disponible
            else:
                print(f"Error {response.status_code}: {response.text[:100]}")
            return None
        except Exception as e:
            print(f"Error consultando {endpoint}: {e}")
            return None
    
    def get_tasa_prestamos_personales(self):
        """Tasa de préstamos personales - LA MÁS IMPORTANTE para tu sistema"""
        dato = self._get("tasa_prestamos_personales")
        if dato:
            return {
                "tasa": float(dato["v"]),
                "fecha": dato["d"]
            }
        return None
    
    def get_inflacion_interanual(self):
        """Inflación interanual"""
        dato = self._get("inflacion_interanual")
        if dato:
            return {
                "inflacion": float(dato["v"]),
                "fecha": dato["d"]
            }
        return None
    
    def get_riesgo_pais(self):
        """Riesgo país (EMBI)"""
        dato = self._get("riesgo_pais")
        if dato:
            return {
                "riesgo_pais": float(dato["v"]),
                "fecha": dato["d"]
            }
        return None
    
    def calcular_tasa_final(self, nivel_riesgo, dti, credit_score, pagos_atrasados):
        """
        Calcula la tasa final para un cliente basada en:
        - Datos reales del BCRA
        - Nivel de riesgo del cliente
        - Perfil crediticio
        """
        
        # Obtener datos reales
        tasa_mercado = self.get_tasa_prestamos_personales()
        inflacion = self.get_inflacion_interanual()
        riesgo_pais = self.get_riesgo_pais()
        
        # Valores por defecto si la API falla
        if tasa_mercado:
            tasa_base_mercado = tasa_mercado["tasa"]
            fecha_dato = tasa_mercado["fecha"]
        else:
            tasa_base_mercado = 85.0
            fecha_dato = datetime.now().strftime("%Y-%m-%d")
        
        inflacion_valor = inflacion["inflacion"] if inflacion else 65.0
        riesgo_pais_valor = riesgo_pais["riesgo_pais"] if riesgo_pais else 1850
        
        # Spreads según nivel de riesgo (basado en mercado argentino real)
        spreads = {
            "Riesgo Bajo": 0.75,    # 25% menos que el promedio del mercado
            "Riesgo Medio": 1.15,   # 15% más que el promedio
            "Riesgo Alto": 2.5      # 150% más que el promedio
        }
        
        spread = spreads.get(nivel_riesgo, 1.15)
        
        # Cálculo base
        tasa_riesgo = tasa_base_mercado * spread
        
        # Ajustes por perfil del cliente
        ajuste_dti = dti * 50          # DTI alto = más tasa
        ajuste_atrasos = pagos_atrasados * 2
        
        if credit_score == "Good":
            ajuste_score = -5          # Descuento
        elif credit_score == "Standard":
            ajuste_score = 0
        else:
            ajuste_score = 8           # Recargo
        
        # Tasa final
        tasa_final = tasa_riesgo + ajuste_dti + ajuste_atrasos + ajuste_score
        
        # Límites para Argentina
        tasa_final = max(35.0, min(tasa_final, 350.0))
        
        # CFT estimado
        cft = round(tasa_final * 1.35, 2)
        
        return {
            "tasa_nominal_anual": round(tasa_final, 2),
            "cft_estimado": cft,
            "tasa_mensual": round(tasa_final / 12, 2),
            "fundamentacion": {
                "tasa_mercado_bcra": tasa_base_mercado,
                "fecha_dato_bcra": fecha_dato,
                "spread_riesgo": f"{spread}x",
                "inflacion_anual": inflacion_valor,
                "riesgo_pais_puntos": riesgo_pais_valor,
                "ajuste_dti": round(ajuste_dti, 2),
                "ajuste_score_crediticio": ajuste_score,
                "ajuste_pagos_atrasados": round(ajuste_atrasos, 2)
            }
        }


# Para probar directamente
if __name__ == "__main__":
    bcra = TasasBCRA()
    
    print("=" * 50)
    print("DATOS REALES DEL BCRA")
    print("=" * 50)
    
    tasa = bcra.get_tasa_prestamos_personales()
    if tasa:
        print(f"✅ Tasa préstamos personales: {tasa['tasa']}% ({tasa['fecha']})")
    
    inflacion = bcra.get_inflacion_interanual()
    if inflacion:
        print(f"✅ Inflación interanual: {inflacion['inflacion']}% ({inflacion['fecha']})")
    
    riesgo = bcra.get_riesgo_pais()
    if riesgo:
        print(f"✅ Riesgo país: {riesgo['riesgo_pais']} puntos ({riesgo['fecha']})")
    
    print()
    print("=" * 50)
    print("EJEMPLOS DE TASAS POR PERFIL")
    print("=" * 50)
    
    # Ejemplo 1: Cliente bueno
    resultado = bcra.calcular_tasa_final("Riesgo Bajo", 0.05, "Good", 0)
    print(f"\n🟢 CLIENTE BAJO RIESGO:")
    print(f"   TNA: {resultado['tasa_nominal_anual']}%")
    print(f"   CFT: {resultado['cft_estimado']}%")
    
    # Ejemplo 2: Cliente medio
    resultado = bcra.calcular_tasa_final("Riesgo Medio", 0.20, "Standard", 2)
    print(f"\n🟡 CLIENTE MEDIO RIESGO:")
    print(f"   TNA: {resultado['tasa_nominal_anual']}%")
    print(f"   CFT: {resultado['cft_estimado']}%")
    
    # Ejemplo 3: Cliente malo
    resultado = bcra.calcular_tasa_final("Riesgo Alto", 0.50, "Poor", 8)
    print(f"\n🔴 CLIENTE ALTO RIESGO:")
    print(f"   TNA: {resultado['tasa_nominal_anual']}%")
    print(f"   CFT: {resultado['cft_estimado']}%")