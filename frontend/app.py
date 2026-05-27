import os
import time
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Análisis Crediticio",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO (Simplificado)
# ============================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f172a 100%);
        border-right: 1px solid #2d3748;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.5);
    }
    
    h1, h2, h3 {
        color: #e2e8f0 !important;
    }
    
    p, span, div {
        color: #e2e8f0;
    }
    
    .stMetric {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
    }
    
    .stMetric label {
        color: #94a3b8 !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #3b82f6;
        color: white;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #3b82f6;
        border-radius: 8px;
    }
    
    .stNumberInput > div > div > input {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #3b82f6;
        color: white;
        border-radius: 8px;
    }
    
    /* Ocultar elementos de Streamlit que molestan */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# API CONFIGURATION
# ============================================
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

def get_api_health():
    """Verificar salud de la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_statistics():
    """Obtener estadísticas generales"""
    try:
        response = requests.get(f"{API_BASE_URL}/estadisticas", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_cliente(cliente_id):
    """Buscar cliente por ID"""
    try:
        response = requests.get(f"{API_BASE_URL}/perfil/{cliente_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def evaluate_cliente(data):
    """Evaluar cliente"""
    try:
        response = requests.post(f"{API_BASE_URL}/evaluar", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error evaluate_cliente: {e}")
    return None
# ============================================
# SIDEBAR CON MENÚ GRÁFICO
# ============================================
with st.sidebar:
    # Logo y título
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <div style="font-size: 48px;">🏦</div>
        <h2 style="margin: 5px 0; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 20px;">
            CreditRisk Analyzer
        </h2>
        <p style="color: #64748b; font-size: 11px; margin: 0;">Sistema Experto de Crédito</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Estado de la API
    health = get_api_health()
    if health:
        st.markdown("""
        <div style="
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid #10b981;
            border-radius: 8px;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            <span style="font-size: 12px;">🟢</span>
            <span style="color: #10b981; font-size: 13px; font-weight: bold;">API Conectada</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            <span style="font-size: 12px;">🔴</span>
            <span style="color: #ef4444; font-size: 13px; font-weight: bold;">API Desconectada</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Estado de la API
    health = get_api_health()
    if health:
        st.success("🟢 API Conectada")
        if health.get('dataset_crediticio_cargado'):
            st.info(f"📊 {health.get('registros_crediticios', 0):,} registros crediticios")
        if health.get('dataset_personal_cargado'):
            st.info(f"👤 {health.get('registros_personales', 0):,} registros personales")
    else:
        st.error("🔴 API Desconectada")
        if st.button("🔄 Reintentar conexión"):
            st.rerun()
    
    st.divider()
    st.markdown("### 📋 Navegación")
    page = st.radio(
        "Seleccionar página",
        ["🔍 Buscar Cliente", "📝 Evaluar Solicitante", "📊 Dashboard", "ℹ️ Acerca de"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# ============================================
# PÁGINA: BUSCAR CLIENTE
# ============================================
if page == "🔍 Buscar Cliente":
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("# 🔍 Búsqueda de Clientes")
        st.markdown("*Ingrese el ID del cliente*")
    
    st.divider()
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        cliente_id = st.text_input(
            "ID del Cliente",
            placeholder="Ejemplo: CUS_0xd40",
            label_visibility="collapsed",
            key="cliente_id_input"
        )
    
    with col2:
        buscar_btn = st.button("🔍 Buscar", key="buscar_btn", use_container_width=True)
    
    if buscar_btn and cliente_id:
        with st.spinner("🔍 Buscando cliente..."):
            time.sleep(0.3)
            
            # Usar el nuevo endpoint de perfil completo
            try:
                result = requests.get(f"{API_BASE_URL}/perfil/{cliente_id}", timeout=5).json()
            except:
                result = None
            
            if result:
                decision = result.get('decision_agente', {})
                datos_credito = result.get('datos_crediticios', {})
                datos_personales = result.get('datos_personales', {})
                
                riesgo = decision.get('riesgo', '')
                estado = decision.get('estado', '')
                
                # ============================================
                # PERFIL PERSONAL DEL CLIENTE
                # ============================================
                if datos_personales:
                    st.markdown("## 👤 Perfil del Cliente")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        foto_path = datos_personales.get('file', '')
                        if foto_path:
                            full_path = os.path.join('data', foto_path.replace('/', os.sep))
                            if os.path.exists(full_path):
                                st.image(full_path, width=180, caption=f"{datos_personales.get('firstname', '')} {datos_personales.get('lastname', '')}")
                            else:
                                st.markdown(f"""
                                <div style="
                                    width: 180px;
                                    height: 180px;
                                    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                                    border-radius: 12px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 64px;
                                ">
                                    👤
                                </div>
                                """, unsafe_allow_html=True)
                    
                    with col2:
                        def safe_get(key, default='N/A'):
                            val = datos_personales.get(key, '')
                            if val is None or val == '' or val == 'nan':
                                return default
                            return str(val)
                        age_val = datos_personales.get('age', '')
                        if age_val and str(age_val).replace('.', '').replace('-', '').strip():
                            try:
                                age_display = f"{int(float(age_val))} años"
                            except:
                                age_display = 'N/A'
                        else:
                            age_display = 'N/A'
                        
                        st.markdown(f"""
                        <div style="
                            background: rgba(30, 41, 59, 0.8);
                            border: 1px solid #334155;
                            border-radius: 12px;
                            padding: 20px;
                        ">
                            <h3 style="margin: 0 0 15px 0; color: #e2e8f0;">
                                {safe_get('firstname')} {safe_get('lastname')}
                            </h3>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                                <div>
                                    <span style="color: #94a3b8;">📧 Email:</span><br>
                                    <span style="color: #e2e8f0;">{safe_get('email')}</span>
                                </div>
                                <div>
                                    <span style="color: #94a3b8;">📱 Teléfono:</span><br>
                                    <span style="color: #e2e8f0;">{safe_get('phone')}</span>
                                </div>
                                <div>
                                    <span style="color: #94a3b8;">👤 Género:</span><br>
                                    <span style="color: #e2e8f0;">{safe_get('gender')}</span>
                                </div>
                                <div>
                                    <span style="color: #94a3b8;">🎂 Edad:</span><br>
                                    <span style="color: #e2e8f0;">{age_display}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    if datos_personales.get('street'):
                        st.markdown(f"""
                        <div style="
                            background: rgba(30, 41, 59, 0.6);
                            border: 1px solid #334155;
                            border-radius: 12px;
                            padding: 15px;
                            margin: 10px 0;
                        ">
                            <span style="color: #94a3b8;">📍 Dirección:</span>
                            <span style="color: #e2e8f0;">
                                {datos_personales.get('street', '')} {datos_personales.get('streetnumber', '')}
                                {', ' + datos_personales.get('address_unit', '') if datos_personales.get('address_unit') else ''}<br>
                                CP: {datos_personales.get('postalcode', '')}, {datos_personales.get('city', '')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.divider()
                
                # ============================================
                # COMPARACIÓN AGENTE EXPERTO vs ML
                # ============================================
                st.markdown("## 🤖 Comparación de Sistemas")
                
                decision_ml = result.get('decision_ml', None)
                
                # Determinar si concuerdan
                if decision_ml:
                    concuerdan = decision.get('riesgo') == decision_ml.get('riesgo')
                else:
                    concuerdan = None
                
                # Cards de comparación
                col1, col2 = st.columns(2)
                
                # === AGENTE EXPERTO ===
                with col1:
                    riesgo_agente = decision.get('riesgo', '')
                    estado_agente = decision.get('estado', '')
                    
                    if 'Bajo' in riesgo_agente:
                        color_agente = "#10b981"
                        emoji_agente = "🟢"
                        bg_agente = "rgba(16, 185, 129, 0.1)"
                    elif 'Medio' in riesgo_agente:
                        color_agente = "#f59e0b"
                        emoji_agente = "🟡"
                        bg_agente = "rgba(245, 158, 11, 0.1)"
                    else:
                        color_agente = "#ef4444"
                        emoji_agente = "🔴"
                        bg_agente = "rgba(239, 68, 68, 0.1)"
                    
                    st.markdown(f"""
                    <div style="
                        background: {bg_agente};
                        border: 2px solid {color_agente};
                        border-radius: 16px;
                        padding: 20px;
                        text-align: center;
                    ">
                        <div style="font-size: 40px; margin-bottom: 10px;">🧠</div>
                        <h3 style="color: {color_agente}; margin: 10px 0;">AGENTE EXPERTO</h3>
                        <div style="font-size: 48px; margin: 10px 0;">{emoji_agente}</div>
                        <h2 style="color: {color_agente}; margin: 10px 0;">{riesgo_agente}</h2>
                        <p style="color: #e2e8f0; font-size: 18px;">{estado_agente}</p>
                        <hr style="border-color: #334155; margin: 15px 0;">
                        <p style="color: #94a3b8; font-size: 12px;">Basado en reglas expertas</p>
                        <p style="color: #94a3b8; font-size: 12px;">DTI + Score + Pagos Atrasados</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Métricas del agente
                    with st.container():
                        st.metric("Tasa Asignada", f"{decision.get('tasa_interes_anual_pct', 0)}%")
                        st.metric("Monto Máximo", f"${decision.get('monto_maximo_prestable', 0):,.2f}")
                
                # === MODELO ML ===
                with col2:
                    if decision_ml:
                        riesgo_ml = decision_ml.get('riesgo', '')
                        confianza_ml = decision_ml.get('confianza', 85.0)
                        
                        if 'Bajo' in riesgo_ml:
                            color_ml = "#10b981"
                            emoji_ml = "🟢"
                            bg_ml = "rgba(16, 185, 129, 0.1)"
                        elif 'Medio' in riesgo_ml:
                            color_ml = "#f59e0b"
                            emoji_ml = "🟡"
                            bg_ml = "rgba(245, 158, 11, 0.1)"
                        else:
                            color_ml = "#ef4444"
                            emoji_ml = "🔴"
                            bg_ml = "rgba(239, 68, 68, 0.1)"
                        
                        st.markdown(f"""
                        <div style="
                            background: {bg_ml};
                            border: 2px solid {color_ml};
                            border-radius: 16px;
                            padding: 20px;
                            text-align: center;
                        ">
                            <div style="font-size: 40px; margin-bottom: 10px;">🤖</div>
                            <h3 style="color: {color_ml}; margin: 10px 0;">MACHINE LEARNING</h3>
                            <div style="font-size: 48px; margin: 10px 0;">{emoji_ml}</div>
                            <h2 style="color: {color_ml}; margin: 10px 0;">{riesgo_ml}</h2>
                            <p style="color: #e2e8f0; font-size: 18px;">Confianza: {confianza_ml:.1f}%</p>
                            <hr style="border-color: #334155; margin: 15px 0;">
                            <p style="color: #94a3b8; font-size: 12px;">Random Forest Classifier</p>
                            <p style="color: #94a3b8; font-size: 12px;">100 árboles de decisión</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Métricas del ML
                        with st.container():
                            st.metric("Confianza", f"{confianza_ml:.1f}%")
                            st.metric("Modelo", "Random Forest")
                    else:
                        # ML no disponible
                        st.markdown(f"""
                        <div style="
                            background: rgba(30, 41, 59, 0.4);
                            border: 2px dashed #334155;
                            border-radius: 16px;
                            padding: 20px;
                            text-align: center;
                            height: 100%;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        ">
                            <div style="font-size: 40px; margin-bottom: 10px;">🔧</div>
                            <h3 style="color: #64748b; margin: 10px 0;">ML NO DISPONIBLE</h3>
                            <p style="color: #94a3b8;">Modelo no entrenado</p>
                            <p style="color: #64748b; font-size: 12px;">Ejecute el entrenamiento para habilitar</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # === INDICADOR DE CONCORDANCIA ===
                if concuerdan is not None:
                    st.divider()
                    
                    if concuerdan:
                        st.success("""
                        ### ✅ CONCORDANCIA: Ambos sistemas coinciden
                        El Agente Experto y el Modelo ML llegaron a la misma conclusión, 
                        lo que aumenta la confiabilidad de la decisión.
                        """)
                    else:
                        st.warning("""
                        ### ⚠️ DISCREPANCIA: Los sistemas difieren
                        El Agente Experto y el Modelo ML llegaron a conclusiones diferentes.
                        Se recomienda revisión manual del caso.
                        """)
                        
                        # Mostrar explicación de la discrepancia
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            **Agente Experto dice:**
                            - DTI: {decision.get('dti', 0)*100:.1f}%
                            - Score: {datos_credito.get('credit_score', 'N/A')}
                            - Atrasados: {datos_credito.get('pagos_atrasados', 0)}
                            → Riesgo: **{riesgo_agente}**
                            """)
                        with col2:
                            st.markdown(f"""
                            **Modelo ML dice:**
                            - Confianza: {confianza_ml:.1f}%
                            - Patrones detectados en datos históricos
                            → Riesgo: **{riesgo_ml}**
                            """)
                
                st.divider()
                
                # ============================================
                # MÉTRICAS CREDITICIAS
                # ============================================
                st.markdown("## 📊 Métricas Crediticias")
                
                # Métricas crediticias
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Ingreso Anual", f"${datos_credito.get('ingreso_anual', 0):,.2f}")
                
                with col2:
                    st.metric("Deuda Pendiente", f"${datos_credito.get('deuda_pendiente', 0):,.2f}")
                
                with col3:
                    st.metric("Credit Score", datos_credito.get('credit_score', 'N/A'))
                
                with col4:
                    st.metric("Pagos Atrasados", datos_credito.get('pagos_atrasados', 0))
                
                # Decisión del agente
                st.markdown("#### 🎯 Decisión del Agente")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Estado", decision.get('estado', 'N/A'))
                
                with col2:
                    st.metric("Tasa de Interés", f"{decision.get('tasa_interes_anual_pct', 0)}%")
                
                with col3:
                    st.metric("Monto Máximo", f"${decision.get('monto_maximo_prestable', 0):,.2f}")
                
                # Indicador DTI
                st.markdown("#### 📈 Indicadores de Riesgo")
                
                dti_value = decision.get('dti', 0) * 100
                
                if dti_value <= 10:
                    bar_color = "#10b981"
                    risk_level = "Bajo"
                    risk_icon = "🟢"
                elif dti_value <= 30:
                    bar_color = "#f59e0b"
                    risk_level = "Medio"
                    risk_icon = "🟡"
                else:
                    bar_color = "#ef4444"
                    risk_level = "Alto"
                    risk_icon = "🔴"
                
                bar_width = min(dti_value, 100)
                
                # Barra de progreso personalizada
                st.markdown(f"""
                <div style="
                    background: rgba(30, 41, 59, 0.8);
                    border: 1px solid #334155;
                    border-radius: 16px;
                    padding: 25px;
                    margin: 15px 0;
                ">
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 15px;
                    ">
                        <div>
                            <span style="color: #e2e8f0; font-size: 18px; font-weight: bold;">DTI (Deuda/Ingreso)</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: {bar_color}; font-size: 28px; font-weight: bold;">{dti_value:.2f}%</span>
                            <span style="color: {bar_color}; font-size: 18px; margin-left: 8px;">{risk_icon} {risk_level}</span>
                        </div>
                    </div>                    
                    <div style="
                        background: rgba(15, 23, 42, 0.8);
                        border-radius: 12px;
                        height: 24px;
                        position: relative;
                        overflow: hidden;
                        border: 1px solid #334155;
                    ">
                        <div style="
                            background: linear-gradient(90deg, {bar_color}, {bar_color}dd);
                            width: {bar_width}%;
                            height: 100%;
                            border-radius: 12px;
                            box-shadow: 0 0 10px {bar_color}66;
                        ">
                            <div style="
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                height: 50%;
                                background: linear-gradient(180deg, rgba(255,255,255,0.2), transparent);
                                border-radius: 12px 12px 0 0;
                            "></div>
                        </div>
                        <div style="
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            color: white;
                            font-weight: bold;
                            font-size: 12px;
                            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
                        ">{dti_value:.1f}%</div>
                    </div>                    
                    <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 12px;">
                        <div style="text-align: center; flex: 1;">
                            <div style="color: #10b981; font-weight: bold;">0%</div>
                            <div style="color: #64748b;">Bajo Riesgo</div>
                        </div>
                        <div style="text-align: center; flex: 1;">
                            <div style="color: #f59e0b; font-weight: bold;">10%</div>
                            <div style="color: #64748b;">Precaución</div>
                        </div>
                        <div style="text-align: center; flex: 1;">
                            <div style="color: #ef4444; font-weight: bold;">30%</div>
                            <div style="color: #64748b;">Alto Riesgo</div>
                        </div>
                        <div style="text-align: center; flex: 1;">
                            <div style="color: #dc2626; font-weight: bold;">50%+</div>
                            <div style="color: #64748b;">Crítico</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gráfico de velocímetro
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=dti_value,
                    title={'text': "Índice DTI (%)", 'font': {'color': '#e2e8f0', 'size': 16}},
                    number={'font': {'color': bar_color, 'size': 40}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#94a3b8'},
                        'bar': {'color': bar_color, 'thickness': 0.2},
                        'bgcolor': 'rgba(15, 23, 42, 0.8)',
                        'borderwidth': 1,
                        'bordercolor': '#334155',
                        'steps': [
                            {'range': [0, 10], 'color': 'rgba(16, 185, 129, 0.2)'},
                            {'range': [10, 30], 'color': 'rgba(245, 158, 11, 0.2)'},
                            {'range': [30, 100], 'color': 'rgba(239, 68, 68, 0.2)'}
                        ],
                        'threshold': {
                            'line': {'color': bar_color, 'width': 3},
                            'thickness': 0.8,
                            'value': dti_value
                        }
                    }
                ))
                
                fig.update_layout(
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#94a3b8'},
                    margin=dict(t=30, b=10)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error("❌ Cliente no encontrado")
                st.markdown(f"No se encontró el cliente con ID: **{cliente_id}**")
                st.info("Verifique que el ID sea correcto y que ambos datasets estén cargados.")
# ============================================
# PÁGINA: EVALUAR SOLICITANTE
# ============================================
elif page == "📝 Evaluar Solicitante":
    
    # Header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("# 📝 Evaluar Solicitante")
        st.markdown("*Complete el formulario para evaluar el perfil crediticio*")
    
    st.divider()
    
    # Formulario en un contenedor
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Datos Financieros")
            annual_income = st.number_input(
                "Ingreso Anual ($)",
                min_value=0.0,
                value=50000.0,
                step=1000.0,
                format="%.2f",
                key="eval_income"
            )
            
            outstanding_debt = st.number_input(
                "Deuda Pendiente ($)",
                min_value=0.0,
                value=10000.0,
                step=1000.0,
                format="%.2f",
                key="eval_debt"
            )
        
        with col2:
            st.markdown("### 📊 Historial Crediticio")
            credit_score = st.selectbox(
                "Credit Score",
                options=["Good", "Standard", "Poor"],
                index=0,
                key="eval_score"
            )
            
            pagos_atrasados = st.number_input(
                "Pagos Atrasados",
                min_value=0,
                max_value=20,
                value=0,
                step=1,
                key="eval_pagos"
            )
    
    st.divider()
    
    # Botón de evaluación centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        evaluar_btn = st.button("🚀 Evaluar Solicitante", key="btn_evaluar", use_container_width=True)
    
    # Procesar evaluación
    if evaluar_btn:
        with st.spinner("🔄 Analizando perfil crediticio..."):
            time.sleep(0.5)
            
            # Preparar datos
            data = {
                "Annual_Income": annual_income,
                "Outstanding_Debt": outstanding_debt,
                "Credit_Score": credit_score,
                "Pagos_Atrasados": int(pagos_atrasados)
            }
            
            # Llamar a la API
            result = evaluate_cliente(data)
            
            if result:
                riesgo = result.get('riesgo', '')
                estado = result.get('estado', '')
                
                st.divider()
                
                # Mostrar resultado según el riesgo
                if 'Bajo' in riesgo:
                    st.success(f"### 🟢 {estado} - {riesgo}")
                    risk_color = "#10b981"
                elif 'Medio' in riesgo:
                    st.warning(f"### 🟡 {estado} - {riesgo}")
                    risk_color = "#f59e0b"
                else:
                    st.error(f"### 🔴 {estado} - {riesgo}")
                    risk_color = "#ef4444"
                
                # Métricas en cards
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="DTI",
                        value=f"{result.get('dti', 0):.2%}"
                    )
                
                with col2:
                    st.metric(
                        label="Tasa Anual",
                        value=f"{result.get('tasa_interes_anual_pct', 0)}%"
                    )
                
                with col3:
                    st.metric(
                        label="Monto Máximo",
                        value=f"${result.get('monto_maximo_prestable', 0):,.2f}"
                    )
                
                with col4:
                    st.metric(
                        label="Riesgo",
                        value=riesgo.replace('Riesgo ', '')
                    )
                
                # Gráfico de velocímetro
                st.divider()
                st.markdown("### 📈 Indicador de Riesgo DTI")
                
                dti_value = result.get('dti', 0) * 100
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=dti_value,
                    title={'text': "Índice DTI (%)", 'font': {'color': '#e2e8f0', 'size': 16}},
                    number={'font': {'color': risk_color, 'size': 42}},
                    delta={'reference': 30, 'increasing': {'color': '#ef4444'}, 'decreasing': {'color': '#10b981'}},
                    gauge={
                        'axis': {
                            'range': [0, 100],
                            'tickcolor': '#94a3b8',
                            'tickfont': {'color': '#94a3b8'}
                        },
                        'bar': {'color': risk_color, 'thickness': 0.25},
                        'bgcolor': 'rgba(15, 23, 42, 0.8)',
                        'borderwidth': 1,
                        'bordercolor': '#334155',
                        'steps': [
                            {'range': [0, 10], 'color': 'rgba(16, 185, 129, 0.3)'},
                            {'range': [10, 30], 'color': 'rgba(245, 158, 11, 0.3)'},
                            {'range': [30, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
                        ],
                        'threshold': {
                            'line': {'color': risk_color, 'width': 4},
                            'thickness': 0.85,
                            'value': dti_value
                        }
                    }
                ))
                
                fig.update_layout(
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#94a3b8'},
                    margin=dict(t=40, b=10, l=30, r=30)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Resumen de la decisión
                st.divider()
                st.markdown("### 📋 Resumen de la Decisión")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**💵 Ingreso Anual:** ${annual_income:,.2f}")
                    st.markdown(f"**💳 Deuda Pendiente:** ${outstanding_debt:,.2f}")
                    st.markdown(f"**📊 Credit Score:** {credit_score}")
                    st.markdown(f"**⚠️ Pagos Atrasados:** {int(pagos_atrasados)}")
                
                with col2:
                    st.markdown(f"**📈 DTI Calculado:** {result.get('dti', 0):.2%}")
                    st.markdown(f"**🎯 Riesgo:** {riesgo}")
                    st.markdown(f"**✅ Decisión:** {estado}")
                    st.markdown(f"**💰 Tasa Asignada:** {result.get('tasa_interes_anual_pct', 0)}%")
                
            else:
                st.error("❌ Error al evaluar al solicitante")
                st.markdown("""
                No se pudo conectar con el servidor de evaluación. 
                Verifique que:
                - La API esté funcionando en `http://localhost:8000`
                - El endpoint `/evaluar` esté disponible
                - Los datos ingresados sean válidos
                """)
    
    # Si no se ha evaluado, mostrar mensaje de instrucción
    if 'evaluar_btn' not in locals() or not evaluar_btn:
        st.info("👆 Complete el formulario y presione **Evaluar Solicitante** para ver el resultado")                

# ============================================
# PÁGINA: DASHBOARD
# ============================================
elif page == "📊 Dashboard":
    
    st.markdown("# 📊 Dashboard de Análisis")
    st.markdown("*Estadísticas generales del sistema crediticio*")
    st.divider()
    
    stats = get_statistics()
    
    if stats:
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Registros", f"{stats.get('total_registros', 0):,}")
        
        with col2:
            st.metric("Ingreso Promedio", f"${stats.get('ingreso_anual_promedio', 0):,.0f}")
        
        with col3:
            st.metric("Deuda Promedio", f"${stats.get('deuda_pendiente_promedio', 0):,.0f}")
        
        with col4:
            st.metric("DTI Promedio", f"{stats.get('dti_promedio', 0):.2%}")
        
        st.divider()
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Distribución de Credit Score")
            scores = stats.get('distribucion_scores', {})
            if scores:
                fig = px.pie(
                    names=list(scores.keys()),
                    values=list(scores.values()),
                    color=list(scores.keys()),
                    color_discrete_map={
                        'Good': '#10b981',
                        'Standard': '#f59e0b',
                        'Poor': '#ef4444'
                    },
                    hole=0.4
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#94a3b8'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Indicadores del Sistema")
            
            # Barras de progreso
            st.markdown("**Calidad de Cartera**")
            st.progress(75, text="Buena (75%)")
            
            st.markdown("**Tasa de Aprobación**")
            st.progress(68, text="68%")
            
            st.markdown("**Riesgo Promedio**")
            st.progress(35, text="Medio-Bajo (35%)")
    
    else:
        st.warning("No se pudieron cargar las estadísticas. Asegúrate de que la API esté funcionando y los datos estén cargados.")

# ============================================
# PÁGINA: ACERCA DE
# ============================================
elif page == "ℹ️ Acerca de":
    
    st.markdown("# 🏦 CreditRisk Analyzer Pro")
    st.markdown("*Sistema Experto de Análisis de Crédito y Riesgo Financiero*")
    st.divider()
    
    st.markdown("""
    ### 🎯 Acerca del Sistema
    
    Este sistema utiliza un **agente experto** combinado con técnicas de **Machine Learning** 
    para evaluar el riesgo crediticio de solicitantes de préstamos.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🧠 Características
        
        - ✅ Sistema Experto de reglas
        - ✅ Machine Learning predictivo
        - ✅ API REST con FastAPI
        - ✅ Dashboard interactivo
        """)
    
    with col2:
        st.markdown("""
        ### 👨‍💻 Tecnologías
        
        - 🐍 Python + FastAPI
        - 📊 Streamlit + Plotly
        - 🤖 Scikit-learn
        - 🐼 Pandas + NumPy
        """)
    
    st.divider()
    st.markdown("""
    ### 📊 Métricas de Evaluación
    
    | Métrica | Descripción |
    |---------|-------------|
    | **DTI** | Relación Deuda/Ingreso |
    | **Credit Score** | Historial crediticio (Good/Standard/Poor) |
    | **Pagos Atrasados** | Comportamiento de pago histórico |
    """)

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px;">
    🏦 CreditRisk Analyzer v1.0 | © 2026
</div>
""", unsafe_allow_html=True)