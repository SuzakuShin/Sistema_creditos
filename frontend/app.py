import os
import time
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="CreditRisk Analyzer Pro",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS PERSONALIZADO 
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
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 30px !important;
        font-weight: bold !important;
        transition: all 0.3s !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.5) !important;
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
    
    /* Sidebar navigation styles */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid transparent;
        margin: 2px 0;
    }
    .nav-btn:hover {
        transform: translateX(5px);
        border-color: #3b82f6;
    }
    .nav-btn.active {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
        border: 1px solid #3b82f6;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
    }
    .nav-btn.inactive {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(51, 65, 85, 0.3);
    }
    .nav-icon {
        font-size: 24px;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        flex-shrink: 0;
    }
    .nav-label {
        color: #e2e8f0;
        font-size: 14px;
        font-weight: 500;
    }
    .nav-desc {
        color: #64748b;
        font-size: 11px;
    }
    .nav-badge {
        background: #3b82f6;
        color: white;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 10px;
        font-weight: bold;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
# FUNCIONES DE API
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

def get_api_health():
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_statistics():
    try:
        r = requests.get(f"{API_BASE_URL}/estadisticas", timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_cliente(cliente_id):
    try:
        r = requests.get(f"{API_BASE_URL}/perfil/{cliente_id}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def evaluate_cliente(data):
    try:
        r = requests.post(f"{API_BASE_URL}/evaluar", json=data, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

# MENÚ
with st.sidebar:    
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
    
    
    # MENÚ DE NAVEGACIÓN 
    st.markdown("""
    <style>
        .nav-container {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .nav-btn-wrapper {
            position: relative;
            margin-bottom: 2px;
        }
        .nav-btn {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 16px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid transparent;
            text-decoration: none;
            margin: 2px 0;
            height: 52px;
            box-sizing: border-box;
        }
        .nav-btn:hover {
            transform: translateX(5px);
            border-color: #3b82f6;
        }
        .nav-btn.active {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
            border: 1px solid #3b82f6;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
        }
        .nav-btn.inactive {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(51, 65, 85, 0.3);
        }
        .nav-icon {
            font-size: 24px;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            flex-shrink: 0;
        }
        .nav-label {
            color: #e2e8f0;
            font-size: 13px;
            font-weight: 500;
        }
        .nav-desc {
            color: #64748b;
            font-size: 10px;
        }
        .nav-badge {
            background: #3b82f6;
            color: white;
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: bold;
        }
        /* Ocultar botones de Streamlit asociados a la navegacion */
        div[data-testid="element-container"]:has(div.nav-btn-wrapper) + div[data-testid="element-container"]:has(button),
        div.element-container:has(div.nav-btn-wrapper) + div.element-container:has(button) {
            display: none !important;
        }
        /* Ocultar el iframe del script binder para que no deje espacio en blanco */
        div[data-testid="element-container"]:has(iframe[width="0"][height="0"]),
        div.element-container:has(iframe[width="0"][height="0"]) {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Páginas
    pages = [
        {"id": "🔍 Buscar Cliente", "icon": "🔍", "label": "Buscar Cliente", "desc": "Consultar perfil y riesgo", "badge": None},
        {"id": "📝 Evaluar Solicitante", "icon": "📝", "label": "Evaluar Solicitante", "desc": "Nuevo análisis crediticio", "badge": None},
        {"id": "📊 Dashboard", "icon": "📊", "label": "Dashboard", "desc": "Estadísticas y métricas", "badge": None},
        {"id": "🤖 Comparar Sistemas", "icon": "🤖", "label": "Comparar Sistemas", "desc": "Agente Experto vs ML", "badge": "ML"},
        {"id": "ℹ️ Acerca de", "icon": "ℹ️", "label": "Acerca de", "desc": "Información del sistema", "badge": None}
    ]
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = pages[0]["id"]
    
    for p in pages:
        is_active = st.session_state.current_page == p["id"]
        active_class = "active" if is_active else "inactive"
        badge_html = f'<span class="nav-badge">{p["badge"]}</span>' if p["badge"] else ''
        
        btn_html = f"""
        <div class="nav-btn-wrapper">
            <div class="nav-btn {active_class}" data-page="{p['label']}">
                <div class="nav-icon" style="background: {'linear-gradient(135deg, #3b82f6, #8b5cf6)' if is_active else 'rgba(51, 65, 85, 0.3)'};">
                    {p['icon']}
                </div>
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: center; text-align: left;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="nav-label">{p['label']}</span>{badge_html}
                    </div>
                    <div class="nav-desc">{p['desc']}</div>
                </div>
                {'<span style="color: #3b82f6; align-self: center;">▸</span>' if is_active else ''}
            </div>
        </div>
        """.replace('\n', '').strip()
        st.markdown(btn_html, unsafe_allow_html=True)
        
        if st.button(p['label'], key=f"nav_btn_{p['id'].replace(' ', '_')}", use_container_width=True):
            st.session_state.current_page = p["id"]
            st.rerun()
            
    # Script para enlazar los clicks de las tarjetas con los botones reales de Streamlit sin pasar por React
    js_binder = """
    <script>
        function bindNavigation() {
            const parentDoc = window.parent.document;
            if (!parentDoc) return;
            
            const cards = parentDoc.querySelectorAll('.nav-btn');
            if (cards.length === 0) return;
            
            const buttons = Array.from(parentDoc.querySelectorAll('button'));
            
            cards.forEach(card => {
                const pageLabel = card.getAttribute('data-page');
                if (!pageLabel) return;
                
                if (card.dataset.navBound === "true") return;
                
                card.addEventListener('click', () => {
                    const targetBtn = buttons.find(btn => btn.textContent.trim() === pageLabel);
                    if (targetBtn) {
                        targetBtn.click();
                    }
                });
                
                card.dataset.navBound = "true";
            });
        }
        setInterval(bindNavigation, 200);
    </script>
    """
    st.components.v1.html(js_binder, height=0, width=0)
    
    page = st.session_state.current_page
    
    st.divider()
    
    clock_html = f"""
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        .info-card {{
            background: rgba(30, 41, 59, 0.4);
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 11px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
        }}
        .info-row:not(:last-child) {{
            margin-bottom: 5px;
        }}
        .info-row span {{
            color: #e2e8f0;
        }}
    </style>
    <div class="info-card">
        <div class="info-row">
            <span>🕐 Hora</span>
            <span id="live-clock">{datetime.now().strftime('%H:%M:%S')}</span>
        </div>
        <div class="info-row">
            <span>🧠 Motor</span>
            <span>Agente Experto</span>
        </div>
        <div class="info-row">
            <span>🤖 ML</span>
            <span>Random Forest</span>
        </div>
    </div>
    <script>
        function updateClock() {{
            const clockEl = document.getElementById("live-clock");
            if (clockEl) {{
                const now = new Date();
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                clockEl.textContent = hours + ":" + minutes + ":" + seconds;
            }}
        }}
        setInterval(updateClock, 1000);
    </script>
    """
    st.components.v1.html(clock_html, height=75)
    
    st.divider()
    
    if st.button("🔄 Refrescar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# PÁGINA: BUSCAR CLIENTE
if page == "🔍 Buscar Cliente":
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("# 🔍 Búsqueda de Clientes")
        st.markdown("*Ingrese el ID del cliente para ver su perfil completo*")
    
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
            result = get_cliente(cliente_id)
            
            if result:
                decision = result.get('decision_agente', {})
                decision_ml = result.get('decision_ml', None)
                datos_credito = result.get('datos_crediticios', {})
                datos_personales = result.get('datos_personales', {})
                
                riesgo = decision.get('riesgo', '')
                estado = decision.get('estado', '')
                
                # PERFIL PERSONAL
                if datos_personales:
                    st.markdown("## 👤 Perfil del Cliente")
                    
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        firstname = datos_personales.get('firstname', '')
                        lastname = datos_personales.get('lastname', '')
                        iniciales = f"{firstname[:1]}{lastname[:1]}".upper() if firstname and lastname else "??"
                        
                        foto_path = datos_personales.get('file', '')
                        foto_encontrada = False
                        
                        if foto_path:
                            posibles_rutas = [
                                os.path.join('data', foto_path.replace('/', os.sep)),
                                os.path.join('data', 'train', os.path.basename(foto_path)),
                            ]
                            for ruta in posibles_rutas:
                                if os.path.exists(ruta):
                                    st.image(ruta, width=180)
                                    st.caption(f"{firstname} {lastname}")
                                    foto_encontrada = True
                                    break
                        
                        if not foto_encontrada:
                            colores_avatar = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
                            color_idx = hash(cliente_id) % len(colores_avatar)
                            color_avatar = colores_avatar[color_idx]
                            
                            st.markdown(f"""
                            <div style="
                                width: 180px;
                                height: 180px;
                                background: linear-gradient(135deg, {color_avatar}, {color_avatar}dd);
                                border-radius: 50%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 64px;
                                color: white;
                                font-weight: bold;
                                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
                            ">
                                {iniciales}
                            </div>
                            <p style="text-align: center; color: #94a3b8; margin-top: 8px;">{firstname} {lastname}</p>
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
                                <div><span style="color: #94a3b8;">📧 Email:</span><br><span style="color: #e2e8f0;">{safe_get('email')}</span></div>
                                <div><span style="color: #94a3b8;">📱 Teléfono:</span><br><span style="color: #e2e8f0;">{safe_get('phone')}</span></div>
                                <div><span style="color: #94a3b8;">👤 Género:</span><br><span style="color: #e2e8f0;">{safe_get('gender')}</span></div>
                                <div><span style="color: #94a3b8;">🎂 Edad:</span><br><span style="color: #e2e8f0;">{age_display}</span></div>
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
                                {safe_get('street')} {safe_get('streetnumber')}
                                {', ' + safe_get('address_unit') if safe_get('address_unit') != 'N/A' else ''}
                                <br>CP: {safe_get('postalcode')}, {safe_get('city')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.divider()
                # COMPARACIÓN AGENTE EXPERTO vs ML
                st.markdown("## 🤖 Comparación de Sistemas")
                
                if decision_ml and decision_ml.get('riesgo'):
                    concuerdan = decision.get('riesgo') == decision_ml.get('riesgo')
                else:
                    concuerdan = None
                
                col1, col2 = st.columns(2)
                
                # Agente Experto
                with col1:
                    if 'Bajo' in riesgo:
                        color_agente, emoji_agente, bg_agente = "#10b981", "🟢", "rgba(16, 185, 129, 0.1)"
                    elif 'Medio' in riesgo:
                        color_agente, emoji_agente, bg_agente = "#f59e0b", "🟡", "rgba(245, 158, 11, 0.1)"
                    else:
                        color_agente, emoji_agente, bg_agente = "#ef4444", "🔴", "rgba(239, 68, 68, 0.1)"
                    
                    st.markdown(f"""
                    <div style="background: {bg_agente}; border: 2px solid {color_agente}; border-radius: 16px; padding: 20px; text-align: center;">
                        <div style="font-size: 40px;">🧠</div>
                        <h3 style="color: {color_agente};">AGENTE EXPERTO</h3>
                        <div style="font-size: 48px;">{emoji_agente}</div>
                        <h2 style="color: {color_agente};">{riesgo}</h2>
                        <p style="color: #e2e8f0; font-size: 18px;">{estado}</p>
                        <hr style="border-color: #334155;">
                        <p style="color: #94a3b8; font-size: 12px;">Basado en reglas expertas</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.metric("Tasa Asignada", f"{decision.get('tasa_interes_anual_pct', 0)}%")
                    if estado == "Rechazado":
                        st.metric("Monto Máximo", "No aplica")
                    else:
                        st.metric("Monto Máximo", f"${decision.get('monto_maximo_prestable', 0):,.2f}")
                
                # Modelo ML
                with col2:
                    if decision_ml and decision_ml.get('riesgo'):
                        riesgo_ml = decision_ml.get('riesgo', '')
                        confianza_ml = decision_ml.get('confianza', 85.0)
                        
                        if 'Bajo' in riesgo_ml:
                            color_ml, emoji_ml, bg_ml = "#10b981", "🟢", "rgba(16, 185, 129, 0.1)"
                        elif 'Medio' in riesgo_ml:
                            color_ml, emoji_ml, bg_ml = "#f59e0b", "🟡", "rgba(245, 158, 11, 0.1)"
                        else:
                            color_ml, emoji_ml, bg_ml = "#ef4444", "🔴", "rgba(239, 68, 68, 0.1)"
                        
                        st.markdown(f"""
                        <div style="background: {bg_ml}; border: 2px solid {color_ml}; border-radius: 16px; padding: 20px; text-align: center;">
                            <div style="font-size: 40px;">🤖</div>
                            <h3 style="color: {color_ml};">MACHINE LEARNING</h3>
                            <div style="font-size: 48px;">{emoji_ml}</div>
                            <h2 style="color: {color_ml};">{riesgo_ml}</h2>
                            <p style="color: #e2e8f0; font-size: 18px;">Confianza: {confianza_ml:.1f}%</p>
                            <hr style="border-color: #334155;">
                            <p style="color: #94a3b8; font-size: 12px;">Random Forest Classifier</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.metric("Confianza", f"{confianza_ml:.1f}%")
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(30,41,59,0.4); border: 2px dashed #334155; border-radius: 16px; padding: 20px; text-align: center;">
                            <div style="font-size: 40px;">🔧</div>
                            <h3 style="color: #64748b;">ML NO DISPONIBLE</h3>
                            <p style="color: #94a3b8;">Modelo no entrenado</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                if concuerdan is True:
                    st.divider()
                    st.success("### ✅ CONCORDANCIA: Ambos sistemas coinciden")
                elif concuerdan is False:
                    st.divider()
                    st.warning("### ⚠️ DISCREPANCIA: Los sistemas difieren")
                st.divider()
                st.markdown("## 📊 Métricas Crediticias")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Ingreso Anual", f"${datos_credito.get('ingreso_anual', 0):,.2f}")
                with col2:
                    st.metric("Deuda Pendiente", f"${datos_credito.get('deuda_pendiente', 0):,.2f}")
                with col3:
                    st.metric("Credit Score", datos_credito.get('credit_score', 'N/A'))
                with col4:
                    st.metric("Pagos Atrasados", datos_credito.get('pagos_atrasados', 0))
                
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

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=dti_value,
                    title={'text': "Índice DTI (%)", 'font': {'color': '#e2e8f0'}},
                    number={'font': {'color': bar_color, 'size': 40}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#94a3b8'},
                        'bar': {'color': bar_color},
                        'steps': [
                            {'range': [0, 10], 'color': 'rgba(16, 185, 129, 0.2)'},
                            {'range': [10, 30], 'color': 'rgba(245, 158, 11, 0.2)'},
                            {'range': [30, 100], 'color': 'rgba(239, 68, 68, 0.2)'}
                        ]
                    }
                ))
                fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': '#94a3b8'})
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error(f"❌ Cliente '{cliente_id}' no encontrado")
# PÁGINA: EVALUAR SOLICITANTE
elif page == "📝 Evaluar Solicitante":
    
    st.markdown("# 📝 Evaluar Solicitante")
    st.markdown("*Complete el formulario para evaluar el perfil crediticio*")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        annual_income = st.number_input("💰 Ingreso Anual ($)", min_value=0.0, value=50000.0, step=1000.0, format="%.2f", key="eval_income_v3")
        outstanding_debt = st.number_input("💳 Deuda Pendiente ($)", min_value=0.0, value=10000.0, step=1000.0, format="%.2f", key="eval_debt_v3")
    
    with col2:
        credit_score = st.selectbox("📊 Credit Score", ["Good", "Standard", "Poor"], key="eval_score_v3")
        pagos_atrasados = st.number_input("⚠️ Pagos Atrasados", min_value=0, max_value=20, value=0, step=1, key="eval_pagos_v3")
    
    st.divider()
    
    if st.button("🚀 Evaluar Solicitante", type="primary", use_container_width=True):
        with st.spinner("Analizando..."):
            time.sleep(0.3)
            
            data = {
                "Annual_Income": annual_income,
                "Outstanding_Debt": outstanding_debt,
                "Credit_Score": credit_score,
                "Pagos_Atrasados": int(pagos_atrasados)
            }
            
            result = evaluate_cliente(data)
            
            if result:
                riesgo = result.get('riesgo', '')
                estado = result.get('estado', '')
                
                st.divider()
                
                if 'Bajo' in riesgo:
                    st.success(f"### 🟢 {estado} - {riesgo}")
                    risk_color = "#10b981"
                elif 'Medio' in riesgo:
                    st.warning(f"### 🟡 {estado} - {riesgo}")
                    risk_color = "#f59e0b"
                else:
                    st.error(f"### 🔴 {estado} - {riesgo}")
                    risk_color = "#ef4444"
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tasa de Interés", f"{result.get('tasa_interes_anual_pct', 0)}%")
                with col2:
                    st.metric("Monto Máximo", f"${result.get('monto_maximo_prestable', 0):,.2f}")
                with col3:
                    st.metric("DTI", f"{result.get('dti', 0):.2%}")                
                # Velocímetro
                dti_value = result.get('dti', 0) * 100
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=dti_value,
                    title={'text': "Índice DTI (%)", 'font': {'color': '#e2e8f0'}},
                    number={'font': {'color': risk_color, 'size': 40}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': risk_color},
                        'steps': [
                            {'range': [0, 10], 'color': 'rgba(16, 185, 129, 0.2)'},
                            {'range': [10, 30], 'color': 'rgba(245, 158, 11, 0.2)'},
                            {'range': [30, 100], 'color': 'rgba(239, 68, 68, 0.2)'}
                        ]
                    }
                ))
                fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': '#94a3b8'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ Error al conectar con la API")

# PÁGINA: DASHBOARD
elif page == "📊 Dashboard":
    
    st.markdown("# 📊 Dashboard de Análisis")
    st.markdown("*Estadísticas generales del sistema crediticio*")
    st.divider()
    
    stats = get_statistics()
    
    if stats:
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Distribución de Credit Score")
            scores = stats.get('distribucion_scores', {})
            if scores:
                fig = px.pie(
                    names=list(scores.keys()),
                    values=list(scores.values()),
                    color=list(scores.keys()),
                    color_discrete_map={'Good': '#10b981', 'Standard': '#f59e0b', 'Poor': '#ef4444'},
                    hole=0.4
                )
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': '#94a3b8'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Indicadores del Sistema")
            st.markdown("**Calidad de Cartera**")
            st.progress(75, text="Buena (75%)")
            st.markdown("**Tasa de Aprobación**")
            st.progress(68, text="68%")
            st.markdown("**Riesgo Promedio**")
            st.progress(35, text="Medio-Bajo (35%)")
    else:
        st.warning("No se pudieron cargar las estadísticas")

# PÁGINA: COMPARAR SISTEMAS
elif page == "🤖 Comparar Sistemas":
    
    st.markdown("# 🤖 Comparación de Sistemas")
    st.markdown("*Agente Experto vs Machine Learning*")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(30,41,59,0.8); border: 2px solid #3b82f6; border-radius: 16px; padding: 25px; text-align: center;">
            <div style="font-size: 48px;">🧠</div>
            <h3>AGENTE EXPERTO</h3>
            <hr style="border-color: #334155;">
            <p style="text-align: left;">
            ✅ <b>Reglas deterministas</b><br>
            ✅ <b>100% explicable</b><br>
            ✅ <b>Sin datos de entrenamiento</b><br>
            ✅ <b>Consistente siempre</b>
            </p>
            <hr style="border-color: #334155;">
            <p style="color: #94a3b8; font-size: 13px;">Evalúa: DTI + Credit Score + Pagos Atrasados</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(30,41,59,0.8); border: 2px solid #8b5cf6; border-radius: 16px; padding: 25px; text-align: center;">
            <div style="font-size: 48px;">🤖</div>
            <h3>MACHINE LEARNING</h3>
            <hr style="border-color: #334155;">
            <p style="text-align: left;">
            ✅ <b>Aprende de 100,000 registros</b><br>
            ✅ <b>Detecta patrones complejos</b><br>
            ✅ <b>Random Forest (100 árboles)</b><br>
            ✅ <b>Accuracy: ~79%</b>
            </p>
            <hr style="border-color: #334155;">
            <p style="color: #94a3b8; font-size: 13px;">5 features | 100 estimadores | Datos reales</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🔄 Flujo de Decisión Híbrido")
    
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="display: inline-block; background: rgba(59,130,246,0.1); border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; margin: 5px;">
            📋 Datos del Cliente
        </div>
        <div style="font-size: 24px;">⬇️</div>
        <div style="display: flex; gap: 20px; justify-content: center;">
            <div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; border-radius: 10px; padding: 15px; flex: 1;">
                🧠 Agente Experto<br><small>Reglas</small>
            </div>
            <div style="background: rgba(139,92,246,0.1); border: 1px solid #8b5cf6; border-radius: 10px; padding: 15px; flex: 1;">
                🤖 Modelo ML<br><small>Random Forest</small>
            </div>
        </div>
        <div style="font-size: 24px;">⬇️</div>
        <div style="display: inline-block; background: rgba(245,158,11,0.1); border: 1px solid #f59e0b; border-radius: 10px; padding: 15px;">
            ✅ Decisión Final + Concordancia
        </div>
    </div>
    """, unsafe_allow_html=True)
# PÁGINA: ACERCA DE
elif page == "ℹ️ Acerca de":
    
    st.markdown("# 🏦 CreditRisk Analyzer")
    st.markdown("*Sistema Experto de Análisis de Crédito y Riesgo Financiero*")
    st.divider()
    
    st.markdown("### 🎯 Acerca del Sistema")
    st.markdown("Este sistema utiliza un **agente experto** combinado con **Machine Learning** para evaluar el riesgo crediticio.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🧠 Características
        - ✅ Sistema Experto de reglas
        - ✅ Machine Learning predictivo
        - ✅ API REST con FastAPI
        - ✅ Dashboard interactivo
        - ✅ Comparación Agente vs ML
        """)
    
    with col2:
        st.markdown("""
        ### 👨‍💻 Tecnologías
        - 🐍 Python + FastAPI
        - 📊 Streamlit + Plotly
        - 🤖 Scikit-learn
        - 🐼 Pandas + NumPy
        - 🐳 Docker
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

# FOOTER
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px;">
    🏦 CreditRisk Analyzer Pro v2.3 | © 2026
</div>
""", unsafe_allow_html=True)