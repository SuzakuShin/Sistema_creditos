# 🧠 Sistema Experto de Scoring Crediticio

API desarrollada en **FastAPI** para evaluar el riesgo crediticio de clientes mediante un agente experto.  
Clasifica automáticamente en **Riesgo Bajo, Medio o Alto** según ingreso anual, deuda pendiente, score crediticio y pagos atrasados.

---

## 👥 Integrantes del equipo
- Ariel Gualla  
- Gabriel Bellesi
- Miriam Velazque

---

## 📌 Descripción del proyecto
Este sistema permite simular la evaluación crediticia de clientes utilizando reglas definidas en un agente experto.  
El objetivo es automatizar la decisión de aprobación, tasa de interés y monto máximo prestable.

---

## 📊 Fuente de datos
- **Dataset:** `clientes_limpios.csv`  
- **Origen:** generado a partir de `data_cleaner.py`  
- **Variables principales:** Annual_Income, Outstanding_Debt, Credit_Score, Pagos_Atrasados

---

## 🎯 Objetivos del análisis
- Evaluar clientes según KPI financieros.  
- Clasificar en Riesgo Bajo, Medio o Alto.  
- Retornar decisión de crédito con tasa y monto máximo.  

---

## 🛠️ Herramientas utilizadas
- **Python 3.10+**  
- **FastAPI**  
- **Uvicorn**  
- **Pandas**  
- **Pydantic**

---

## 🔄 Proceso de análisis
1. Limpieza de datos con `data_cleaner.py`.  
2. Carga del dataset en memoria al iniciar la API.  
3. Evaluación de clientes vía endpoint `/evaluar`.  
4. Retorno de decisión en formato JSON.  

---

## 📈 Resultados principales
- Riesgo Bajo → Aprobado, tasa 15%, monto máximo 50% del ingreso anual.  
- Riesgo Medio → Aprobado condicional, tasa 25%, monto máximo 30% del ingreso anual.  
- Riesgo Alto → Rechazado, tasa 40%, monto máximo 10% del ingreso anual.  

---

## 📊 Visualizaciones
Ejemplo de respuesta del endpoint `/evaluar`:

```json
{
  "riesgo": "Riesgo Bajo",
  "estado": "Aprobado",
  "tasa_interes_anual_pct": 15,
  "monto_maximo_prestable": 100000,
  "dti": 0.05
}
