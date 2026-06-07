#  CreditRisk Analyzer Pro v2.3

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.110-green?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.32-red?style=for-the-badge&logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/Scikit--learn-1.4-orange?style=for-the-badge&logo=scikitlearn" alt="Scikit-learn">
  <img src="https://img.shields.io/badge/ROC_AUC-0.91-brightgreen?style=for-the-badge" alt="ROC AUC">
</p>

<p align="center">
  <b>Sistema Experto de Análisis de Crédito y Riesgo Financiero</b><br>
  <i>API REST + Dashboard interactivo con Agente Experto y Machine Learning</i>
</p>

---

<div align="center">

## 👥 Integrantes

<table>
  <tr>
    <td align="center"><b>Ariel Gualla</b></td>
    <td align="center"><b>Gabriel Bellesi</b></td>
    <td align="center"><b>Miriam Velazque</b></td>
  </tr>
  <tr>
    <td align="center">Desarrollo Backend<br>Machine Learning</td>
    <td align="center">Frontend<br>Data Engineering</td>
    <td align="center">Agente Experto<br>Dashboard</td>
  </tr>
</table>

</div>

---

## 📌  Descripción del Proyecto

<table>
<tr>
<td width="70%">

**CreditRisk Analyzer Pro** automatiza la evaluación de solicitudes de préstamos bancarios analizando el perfil financiero de cada cliente para determinar:

- 🎯 **Nivel de riesgo** (Bajo, Medio, Alto)
- ✅ **Decisión crediticia** (Aprobado, Aprobado condicional, Rechazado)
- 💰 **Tasa de interés personalizada**
- 📊 **Monto máximo prestable**

</td>
<td width="30%" align="center">
<img src="https://politecnico.ar/campus/pluginfile.php/1/core_admin/logocompact/300x300/1774350287/user.jpg" alt="Python">

</td>
</tr>
</table>

---

## 🧠 Dos Motores en Paralelo

<table>
<tr>
<td width="50%" align="center">

### 🧠 Agente Experto
**Scorecard 0-100 puntos**

| Característica | Valor |
|:---|:---|
| Método | Reglas deterministas |
| Explicabilidad | 100% |
| Variables | DTI + Score + Pagos |
| Condiciones | Hard Rules (>5 atrasos = rechazo) |

</td>
<td width="50%" align="center">

### 🤖 Machine Learning
**Random Forest Classifier**

| Característica | Valor |
|:---|:---|
| Algoritmo | Random Forest |
| Árboles | 150 |
| Features | 11 variables |
| ROC AUC | **0.91** |

</td>
</tr>
</table>

---

## 📊 Fuente de Datos

<table>
<tr>
  <th>Dataset</th>
  <th>Registros</th>
  <th>Origen</th>
  <th>Descripción</th>
</tr>
<tr>
  <td><code>clientes.csv</code></td>
  <td align="center">100,000</td>
  <td>Original</td>
  <td>Datos crediticios crudos con 28 columnas</td>
</tr>
<tr>
  <td><code>clientes_limpios.csv</code></td>
  <td align="center">100,000</td>
  <td><code>data_cleaner.py</code></td>
  <td>Datos normalizados y sin caracteres basura</td>
</tr>
<tr>
  <td><code>Datos_personales.csv</code></td>
  <td align="center">12,500</td>
  <td>Externo</td>
  <td>Perfiles con datos demográficos y fotos</td>
</tr>
<tr>
  <td><code>credit_risk_dataset.csv</code></td>
  <td align="center">32,581</td>
  <td>Kaggle</td>
  <td>Target real: <code>loan_status</code> (pagó/no pagó)</td>
</tr>
</table>

---

## 🎯 Objetivos del Análisis

<div style="display: grid; gap: 10px; align-items: left;">

<div style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6;">
✅ Evaluar clientes según KPIs: <b>DTI, Credit Score, Pagos Atrasados</b>
</div>

<div style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981;">
✅ Clasificar en <b>Riesgo Bajo, Medio o Alto</b> mediante scorecard
</div>

<div style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">
✅ Predecir <b>probabilidad de default</b> con Machine Learning
</div>

<div style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
✅ Comparar decisiones para <b>mayor confiabilidad</b>
</div>

</div>

---

## 🏗️ Arquitectura del Sistema

<pre style="background: #0f172a; color: #e2e8f0; padding: 20px; border-radius: 10px;">
┌──────────────────────────────────────────────────────────────┐
│                  <span style="color: #f59e0b;">FRONTEND Streamlit :8501)</span>                   |
│  Búsqueda Clientes │ Evaluación │ Dashboard │ Comparación    │
└──────────────────────────┬───────────────────────────────────┘
                           │ <span style="color: #3b82f6;">REST API (JSON)</span>
┌──────────────────────────┴───────────────────────────────────┐
│                  <span style="color: #10b981;">BACKEND (FastAPI :8000)</span>                       │
│  ┌────────────────────┐  ┌──────────────────────────────┐  
│  │ <span style="color: #f59e0b;">🧠 AGENTE EXPERTO</span> │   │ <span style="color: #8b5cf6;">🤖 MACHINE LEARNING</span>        │   │
│  │ Scorecard 0-100pts  │  │ Random Forest 150 árboles    │   │
│  │ Reglas + Hard Rules │  │ ROC AUC: 0.91               │   │
│  └────────────────────┘  └──────────────────────────────┘   │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────┴───────────────────────────────────┐
│                    <span style="color: #64748b;">CAPA DE DATOS</span>                             │
│  clientes.csv │ limpios.csv │ personales.csv │ modelo.pkl    │
└──────────────────────────────────────────────────────────────┘
</pre>

---

## 🛠️ Stack Tecnológico

<table>
<tr>
  <th>Capa</th>
  <th>Tecnología</th>
  <th>Versión</th>
  <th>Propósito</th>
</tr>
<tr>
  <td>Lenguaje</td>
  <td><img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python"></td>
  <td align="center">3.12</td>
  <td>Desarrollo principal</td>
</tr>
<tr>
  <td>API</td>
  <td><img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI"></td>
  <td align="center">0.110</td>
  <td>Endpoints REST</td>
</tr>
<tr>
  <td>Frontend</td>
  <td><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit"></td>
  <td align="center">1.32</td>
  <td>Dashboard interactivo</td>
</tr>
<tr>
  <td>ML</td>
  <td><img src="https://img.shields.io/badge/Scikit--learn-F7931E?style=flat&logo=scikitlearn&logoColor=white" alt="Scikit-learn"></td>
  <td align="center">1.4</td>
  <td>Random Forest</td>
</tr>
<tr>
  <td>Datos</td>
  <td><img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas"></td>
  <td align="center">2.2</td>
  <td>Procesamiento ETL</td>
</tr>
<tr>
  <td>Gráficos</td>
  <td><img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly"></td>
  <td align="center">5.18</td>
  <td>Velocímetros y charts</td>
</tr>
<tr>
  <td>Contenedores</td>
  <td><img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker"></td>
  <td align="center">Latest</td>
  <td>Orquestación</td>
</tr>
</table>

---
### 1️⃣ Limpieza de Datos (`data_cleaner.py`)

<pre style="background: #0f172a; color: #e2e8f0; padding: 20px; border-radius: 10px;">
<span style="color: #f59e0b;">clientes.csv (100K registros)</span>
    │
    ▼
<span style="color: #3b82f6;">Eliminar duplicados</span>
    │
    ▼
<span style="color: #3b82f6;">Limpiar caracteres especiales</span> (!@#%, _)
    │
    ▼
<span style="color: #3b82f6;">Normalizar valores numéricos</span> (formato europeo)
    │
    ▼
<span style="color: #3b82f6;">Rellenar nulos</span> (mediana/moda)
    │
    ▼
<span style="color: #3b82f6;">Calcular features derivadas</span> (Monthly_Income, DTI)
    │
    ▼
<span style="color: #10b981;">clientes_limpios.csv</span>
</pre>

---

### 2️⃣ Agente Experto (`agent.py`)

<div style="background: #1e293b; padding: 20px; border-radius: 10px;">

<b>Scorecard de Crédito (0-100 puntos)</b>

<table>
<tr>
  <th>Componente</th>
  <th>Puntaje Máx</th>
  <th>Criterio</th>
</tr>
<tr>
  <td>📊 DTI Mensual</td>
  <td align="center"><b>25 pts</b></td>
  <td>Cuota estimada / Ingreso mensual</td>
</tr>
<tr>
  <td>📈 Credit Score</td>
  <td align="center"><b>35 pts</b></td>
  <td>Good = 35 | Standard = 18 | Poor = 0</td>
</tr>
<tr>
  <td>⚠️ Pagos Atrasados</td>
  <td align="center"><b>40 pts</b></td>
  <td>0=40 | 1=25 | 2=12 | 3-5=3 | >5=0</td>
</tr>
</table>

<div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 10px; margin: 15px 0; border-radius: 4px;">
🚫 <b>Condición de Corte (Hard Rule):</b> Más de 5 pagos atrasados = <span style="color: #ef4444;">Rechazo Automático (0 puntos)</span>
</div>

<b>Clasificación Final:</b>

<table>
<tr>
  <th>Puntaje</th>
  <th>Riesgo</th>
  <th>Decisión</th>
  <th>Tasa</th>
  <th>Monto Máx</th>
</tr>
<tr style="background: rgba(16, 185, 129, 0.1);">
  <td align="center">≥ 75</td>
  <td>🟢 Bajo</td>
  <td>Aprobado</td>
  <td>15%</td>
  <td>50% ingreso</td>
</tr>
<tr style="background: rgba(245, 158, 11, 0.1);">
  <td align="center">45-74</td>
  <td>🟡 Medio</td>
  <td>Aprobado condicional</td>
  <td>25%</td>
  <td>30% ingreso</td>
</tr>
<tr style="background: rgba(239, 68, 68, 0.1);">
  <td align="center">< 45</td>
  <td>🔴 Alto</td>
  <td>Rechazado</td>
  <td>0%</td>
  <td>$0</td>
</tr>
</table>

</div>

---

### 3️⃣ Machine Learning (`ml_model.py`)

<div style="background: #1e293b; padding: 20px; border-radius: 10px;">

<b>🎯 Dataset:</b> Credit Risk Dataset (Kaggle) - 32,581 registros con target real

<b>📊 Features utilizadas (11 variables):</b>

<pre style="background: #0f172a; color: #10b981; padding: 15px; border-radius: 8px;">
Annual_Income | Outstanding_Debt | monthly_income | debt_to_income
loan_int_rate | person_emp_length | cb_person_cred_hist_length
credit_score_encoded | home_ownership_encoded
default_on_file | delayed_payments
</pre>

<b>🌲 Hiperparámetros del Random Forest:</b>

<table>
<tr><th>Parámetro</th><th>Valor</th></tr>
<tr><td>n_estimators</td><td align="center">150</td></tr>
<tr><td>max_depth</td><td align="center">12</td></tr>
<tr><td>min_samples_split</td><td align="center">20</td></tr>
<tr><td>min_samples_leaf</td><td align="center">10</td></tr>
<tr><td>class_weight</td><td align="center">balanced</td></tr>
</table>

<b>📈 Métricas de Evaluación:</b>

<table>
<tr>
  <th>Métrica</th>
  <th>Valor</th>
  <th>Interpretación</th>
</tr>
<tr>
  <td>Accuracy</td>
  <td align="center"><b>87.44%</b></td>
  <td>Acierta en ~9 de cada 10 casos</td>
</tr>
<tr>
  <td>ROC AUC</td>
  <td align="center"><b>0.9099</b></td>
  <td>Excelente capacidad discriminativa</td>
</tr>
<tr>
  <td>Precision (No Pagó)</td>
  <td align="center">70%</td>
  <td>Cuando dice "no pagará", acierta 7/10</td>
</tr>
<tr>
  <td>Recall (No Pagó)</td>
  <td align="center">74%</td>
  <td>Detecta 3/4 de los que no pagarán</td>
</tr>
</table>

<b>📊 Importancia de Features:</b>

<pre style="background: #0f172a; color: #e2e8f0; padding: 15px; border-radius: 8px;">
<span style="color: #f59e0b;">debt_to_income</span>           : 25.7% █████████████
<span style="color: #f59e0b;">loan_int_rate</span>            : 18.3% █████████
<span style="color: #f59e0b;">monthly_income</span>           : 12.3% ██████
<span style="color: #f59e0b;">credit_score_encoded</span>     : 11.0% █████
<span style="color: #f59e0b;">Annual_Income</span>            : 10.8% █████
<span style="color: #f59e0b;">home_ownership_encoded</span>   :  9.6% ████
</pre>

</div>

---

### 4️⃣ API REST (`main.py`)

<table>
<tr>
  <th>Método</th>
  <th>Endpoint</th>
  <th>Descripción</th>
</tr>
<tr>
  <td><span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">GET</span></td>
  <td><code>/health</code></td>
  <td>Estado del sistema y datasets cargados</td>
</tr>
<tr>
  <td><span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">GET</span></td>
  <td><code>/estadisticas</code></td>
  <td>Métricas globales (ingresos, deudas, scores)</td>
</tr>
<tr>
  <td><span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">GET</span></td>
  <td><code>/perfil/{cliente_id}</code></td>
  <td>Perfil completo + Agente + ML + Concordancia</td>
</tr>
<tr>
  <td><span style="background: #3b82f6; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">POST</span></td>
  <td><code>/evaluar</code></td>
  <td>Evaluación de nuevo solicitante</td>
</tr>
</table>

---

### 5️⃣ Dashboard (`frontend/app.py`)

<table>
<tr>
  <th>Página</th>
  <th>Funcionalidad</th>
</tr>
<tr>
  <td>🔍 <b>Buscar Cliente</b></td>
  <td>Perfil con foto, datos personales, comparación Agente vs ML lado a lado</td>
</tr>
<tr>
  <td>📝 <b>Evaluar Solicitante</b></td>
  <td>Formulario para nuevos clientes con velocímetro DTI interactivo</td>
</tr>
<tr>
  <td>📊 <b>Dashboard</b></td>
  <td>KPIs, gráfico de torta Credit Score, indicadores de cartera</td>
</tr>
<tr>
  <td>🤖 <b>Comparar Sistemas</b></td>
  <td>Explicación detallada de ambos motores y flujo híbrido de decisión</td>
</tr>
<tr>
  <td>ℹ️ <b>Acerca de</b></td>
  <td>Información del proyecto, características y tecnologías</td>
</tr>
</table>

---

## 📈 Resultados

### Ejemplos del Scorecard

<table>
<tr>
  <th>Ingreso</th>
  <th>Deuda</th>
  <th>Score</th>
  <th>Atrasos</th>
  <th>Puntaje</th>
  <th>Riesgo</th>
  <th>Decisión</th>
  <th>Monto Máx</th>
</tr>
<tr style="background: rgba(16, 185, 129, 0.1);">
  <td>$100,000</td>
  <td>$5,000</td>
  <td>Good</td>
  <td align="center">0</td>
  <td align="center"><b>100</b></td>
  <td>🟢 Bajo</td>
  <td>Aprobado</td>
  <td>$50,000</td>
</tr>
<tr style="background: rgba(16, 185, 129, 0.1);">
  <td>$60,000</td>
  <td>$10,000</td>
  <td>Standard</td>
  <td align="center">0</td>
  <td align="center"><b>83</b></td>
  <td>🟢 Bajo</td>
  <td>Aprobado</td>
  <td>$30,000</td>
</tr>
<tr style="background: rgba(245, 158, 11, 0.1);">
  <td>$60,000</td>
  <td>$20,000</td>
  <td>Standard</td>
  <td align="center">2</td>
  <td align="center"><b>62</b></td>
  <td>🟡 Medio</td>
  <td>Condicional</td>
  <td>$18,000</td>
</tr>
<tr style="background: rgba(239, 68, 68, 0.1);">
  <td>$100,000</td>
  <td>$5,000</td>
  <td>Good</td>
  <td align="center">20</td>
  <td align="center"><b>0</b></td>
  <td>🔴 Alto</td>
  <td>Rechazado</td>
  <td>$0</td>
</tr>
</table>

---

## 📊 Ejemplo de Respuesta API

<details open>
<summary><b>GET /perfil/CUS_0xd40</b></summary>

```json
{
  "Customer_ID": "CUS_0xd40",
  "datos_personales": {
    "firstname": "Bethany",
    "lastname": "Campos",
    "email": "darlene@example.net",
    "city": "Lynnbury",
    "age": 51,
    "phone": "(320) 490-3693"
  },
  "datos_crediticios": {
    "ingreso_anual": 19114.12,
    "deuda_pendiente": 809.98,
    "credit_score": "Good",
    "pagos_atrasados": 7,
    "dti": 0.0424
  },
  "decision_agente": {
    "riesgo": "Riesgo Alto",
    "estado": "Rechazado",
    "tasa_interes_anual_pct": 0,
    "monto_maximo_prestable": 0,
    "score_crediticio": 0
  },
  "decision_ml": {
    "riesgo": "Riesgo Alto",
    "confianza": 90.3,
    "modelo": "Random Forest - Credit Risk Dataset",
    "roc_auc": 0.91,
    "accuracy": 87.44
  },
  "concordancia": true
}