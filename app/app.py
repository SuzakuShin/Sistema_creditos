import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import os

st.set_page_config(page_title="Dashboard de Crédito", layout="wide")


st.title("🏦 Dashboard de Análisis de Crédito")
st.markdown("---")

@st.cache_data
def load_statistics():
    try:
        response = requests.get("http://localhost:8000/estadisticas")
        return response.json()
    except:
        
        return generate_sample_data()

def generate_sample_data():
    import numpy as np
    n = 1000
    data = pd.DataFrame({
        'Annual_Income': np.random.normal(50000, 20000, n),
        'Outstanding_Debt': np.random.normal(15000, 8000, n),
        'Credit_Score': np.random.choice(['Good', 'Standard', 'Poor'], n, p=[0.3, 0.5, 0.2])
    })
    data['DTI'] = data['Outstanding_Debt'] / data['Annual_Income']
    return data

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribución de Credit Score")
    try:
        stats = load_statistics()
        if isinstance(stats, dict):
            scores = stats.get('distribucion_scores', {'Good': 300, 'Standard': 500, 'Poor': 200})
            fig = px.pie(values=list(scores.values()), names=list(scores.keys()), 
                        title="Distribución de Scores")
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("No se pueden cargar las estadísticas")

with col2:
    st.subheader("💰 Métricas Principales")
    try:
        if isinstance(stats, dict):
            metrics = {
                "Ingreso Promedio": f"${stats.get('ingreso_anual_promedio', 50000):,.2f}",
                "Deuda Promedio": f"${stats.get('deuda_pendiente_promedio', 15000):,.2f}",
                "DTI Promedio": f"{stats.get('dti_promedio', 0.3):.2%}"
            }
            for metric, value in metrics.items():
                st.metric(label=metric, value=value)
    except:
        st.error("No se pueden cargar las métricas")

st.markdown("---")
st.subheader("📝 Evaluar Cliente")


with st.form("credit_evaluation"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ingreso_anual = st.number_input("Ingreso Anual ($)", min_value=0.0, value=50000.0)
    with col2:
        deuda = st.number_input("Deuda Pendiente ($)", min_value=0.0, value=10000.0)
    with col3:
        credit_score = st.selectbox("Credit Score", ['Good', 'Standard', 'Poor'])
    
    pagos_atrasados = st.slider("Pagos Atrasados", 0, 10, 0)
    
    submitted = st.form_submit_button("Evaluar Cliente")
    
    if submitted:
        data = {
            "Annual_Income": ingreso_anual,
            "Outstanding_Debt": deuda,
            "Credit_Score": credit_score,
            "Pagos_Atrasados": pagos_atrasados
        }
        
        try:
            response = requests.post("http://localhost:8000/evaluar", json=data)
            if response.status_code == 200:
                result = response.json()
                
               
                st.success("✅ Evaluación completada")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nivel de Riesgo", result['riesgo'])
                with col2:
                    st.metric("Decisión", result['estado'])
                with col3:
                    st.metric("Tasa de Interés", f"{result['tasa_interes_anual_pct']}%")
                
                st.info(f"Monto máximo prestable: ${result['monto_maximo_prestable']:,.2f}")
                st.caption(f"DTI calculado: {result['dti']:.2%}")
        except Exception as e:
            st.error(f"Error al evaluar: {str(e)}")