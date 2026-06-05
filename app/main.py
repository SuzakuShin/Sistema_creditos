from asyncio import transports
from asyncio import transports
import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from .ml_model import CreditRiskModel
from .schemas import ClienteEval, DecisionResponse
from .agent import evaluar_cliente

df_limpio = None
df_personal = None
ml_model = CreditRiskModel()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df_limpio, df_personal
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', 'data')
    
    credit_path = os.path.join(data_dir, 'clientes_limpios.csv')
    print(f"Buscando dataset crediticio en: {credit_path}")
    
    if os.path.exists(credit_path):
        try:
            df_limpio = pd.read_csv(credit_path, low_memory=False)
            print(f"✅ Dataset crediticio cargado: {len(df_limpio)} registros")
        except Exception as e:
            print(f"❌ Error al cargar dataset crediticio: {e}")
            original_path = os.path.join(data_dir, 'clientes.csv')
            if os.path.exists(original_path):
                try:
                    df_limpio = pd.read_csv(original_path, low_memory=False)
                    print(f"⚠️ Cargado dataset original como fallback: {len(df_limpio)} registros")
                except Exception as e2:
                    print(f"❌ Error también con dataset original: {e2}")
                    df_limpio = pd.DataFrame()
            else:
                df_limpio = pd.DataFrame()
    else:
        print(f"⚠️ No se encontró {credit_path}")
        original_path = os.path.join(data_dir, 'clientes.csv')
        if os.path.exists(original_path):
            try:
                df_limpio = pd.read_csv(original_path, low_memory=False)
                print(f"⚠️ Cargado dataset original: {len(df_limpio)} registros")
            except Exception as e:
                print(f"❌ Error al cargar dataset original: {e}")
                df_limpio = pd.DataFrame()
        else:
            df_limpio = pd.DataFrame()
    personal_path = os.path.join(data_dir, 'Datos_personales.csv')
    print(f"Buscando dataset personal en: {personal_path}")
    
    if os.path.exists(personal_path):
        try:
            try:
                df_personal = pd.read_csv(personal_path, sep=';', low_memory=False)
            except:
                df_personal = pd.read_csv(personal_path, sep=',', low_memory=False)
            
            print(f"✅ Dataset personal cargado: {len(df_personal)} registros")
            print(f"   Columnas: {list(df_personal.columns)}")
        except Exception as e:
            print(f"❌ Error al cargar dataset personal: {e}")
            df_personal = pd.DataFrame()
    else:
        print(f"⚠️ No se encontró {personal_path}")
        df_personal = pd.DataFrame()
    
    yield
    
    df_limpio = None
    df_personal = None


app = FastAPI(
    title="Sistema Experto de Scoring Crediticio",
    description="API para evaluar riesgo crediticio mediante un agente de decisión.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", tags=["Salud del Sistema"])
def health_check():
    return {
        "status": "ok",
        "dataset_crediticio_cargado": df_limpio is not None and not df_limpio.empty,
        "dataset_personal_cargado": df_personal is not None and not df_personal.empty,
        "registros_crediticios": len(df_limpio) if df_limpio is not None else 0,
        "registros_personales": len(df_personal) if df_personal is not None else 0
    }


@app.post("/evaluar", response_model=DecisionResponse, tags=["Evaluación Crediticia"])
def evaluar(cliente: ClienteEval):
    decision = evaluar_cliente(
        ingreso_anual=cliente.Annual_Income,
        deuda_pendiente=cliente.Outstanding_Debt,
        credit_score=cliente.Credit_Score,
        pagos_atrasados=cliente.Pagos_Atrasados
    )
    return decision


@app.get("/perfil/{cliente_id}", tags=["Consultas de Clientes"])
def obtener_perfil_completo(cliente_id: str):
    # Verificar datasets
    if df_limpio is None or df_limpio.empty:
        raise HTTPException(status_code=503, detail="Dataset crediticio no disponible. Ejecute data_cleaner.py primero.")
    
    # Buscar en datos crediticios (por Customer_ID o ID)
    cliente_credito = None
    if 'Customer_ID' in df_limpio.columns:
        cliente_credito = df_limpio[df_limpio['Customer_ID'] == cliente_id]
    
    if (cliente_credito is None or cliente_credito.empty) and 'ID' in df_limpio.columns:
        cliente_credito = df_limpio[df_limpio['ID'] == cliente_id]
    
    if cliente_credito is None or cliente_credito.empty:
        raise HTTPException(status_code=404, detail=f"Cliente '{cliente_id}' no encontrado en datos crediticios")
    
    # Tomar el primer registro
    datos_credito = cliente_credito.iloc[0]
    
    # Obtener pagos atrasados de forma segura
    pagos_atrasados = 0
    if 'Num_of_Delayed_Payment' in datos_credito.index:
        try:
            val = datos_credito['Num_of_Delayed_Payment']
            pagos_atrasados = int(float(val)) if pd.notna(val) else 0
        except (ValueError, TypeError):
            pagos_atrasados = 0
    elif 'Delay_from_due_date' in datos_credito.index:
        try:
            val = datos_credito['Delay_from_due_date']
            pagos_atrasados = int(float(val)) if pd.notna(val) else 0
        except (ValueError, TypeError):
            pagos_atrasados = 0
    
    # Obtener valores de forma segura
    try:
        ingreso_anual = float(datos_credito['Annual_Income'])
    except (ValueError, TypeError):
        ingreso_anual = 0.0
    
    try:
        deuda_pendiente = float(datos_credito['Outstanding_Debt'])
    except (ValueError, TypeError):
        deuda_pendiente = 0.0
    
    credit_score_str = str(datos_credito.get('Credit_Score', 'Standard'))
    
    # ============================================
    # EVALUACIÓN DEL AGENTE EXPERTO
    # ============================================
    try:
        decision_agente = evaluar_cliente(
            ingreso_anual=ingreso_anual,
            deuda_pendiente=deuda_pendiente,
            credit_score=credit_score_str,
            pagos_atrasados=pagos_atrasados
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al evaluar cliente con agente experto: {str(e)}")
    
    # ============================================
    # EVALUACIÓN DEL MODELO ML
    # ============================================
    decision_ml = None
    
    try:
        from .ml_model import CreditRiskModel
        ml = CreditRiskModel()
        
        # Calcular DTI
        if ingreso_anual > 0:
            dti = deuda_pendiente / ingreso_anual
        else:
            dti = 1.0
        
        # Preparar datos para ML
        ml_data = {
            'Annual_Income': ingreso_anual,
            'Outstanding_Debt': deuda_pendiente,
            'monthly_income': ingreso_anual / 12.0,
            'debt_to_income': dti,
            'Credit_Score': credit_score_str,
            'delayed_payments': pagos_atrasados 
        }        
        ml_prediction = ml.predict(ml_data)
        
        if ml_prediction is not None:
            risk_labels = {0: "Riesgo Bajo", 1: "Riesgo Medio", 2: "Riesgo Alto"}
            
            # Obtener confianza de la predicción
            confianza = 85.0  # Default
            try:
                features = ml._prepare_features(ml_data)
                if hasattr(ml.model, 'predict_proba'):
                    proba = ml.model.predict_proba(features)
                    confianza = float(proba.max() * 100)
            except Exception:
                # Si no se puede obtener probabilidad, usar valor default
                pass
            
            decision_ml = {
                "riesgo": risk_labels.get(ml_prediction, "Riesgo Medio"),
                "confianza": round(confianza, 1),
                "modelo": "Random Forest Classifier",
                "estimadores": 100
            }
    except ImportError:
        print("⚠️ Módulo ML no encontrado. Omitiendo evaluación ML.")
    except Exception as e:
        print(f"⚠️ Error en evaluación ML: {e}")
    
    # ============================================
    # CONSTRUIR RESPUESTA COMPLETA
    # ============================================
    response = {
        "Customer_ID": cliente_id,
        "datos_crediticios": {
            "ingreso_anual": ingreso_anual,
            "deuda_pendiente": deuda_pendiente,
            "credit_score": credit_score_str,
            "pagos_atrasados": pagos_atrasados,
            "dti": round(deuda_pendiente / ingreso_anual, 4) if ingreso_anual > 0 else 1.0,
            "ingreso_mensual": round(ingreso_anual / 12.0, 2)
        },
        "decision_agente": decision_agente,
        "decision_ml": decision_ml,
        "concordancia": (
            decision_agente.get('riesgo') == decision_ml.get('riesgo')
            if decision_ml else None
        )
    }
    
    # ============================================
    # AGREGAR DATOS PERSONALES SI EXISTEN
    # ============================================
    if df_personal is not None and not df_personal.empty:
        cliente_personal = None
        
        # Probar diferentes nombres de columna para el ID
        for col in ['person_id', 'Person_ID', 'Customer_ID', 'ID']:
            if col in df_personal.columns:
                cliente_personal = df_personal[df_personal[col] == cliente_id]
                if not cliente_personal.empty:
                    break
        
        if cliente_personal is not None and not cliente_personal.empty:
            datos_personales = cliente_personal.iloc[0]
            response["datos_personales"] = {}
            
            # Mapeo de campos de forma segura
            campos_map = {
                'firstname': ['firstname', 'FirstName', 'first_name', 'nombre'],
                'lastname': ['lastname', 'LastName', 'last_name', 'apellido'],
                'gender': ['gender', 'Gender', 'sexo'],
                'age': ['age', 'Age', 'edad'],
                'street': ['street', 'Street', 'calle'],
                'streetnumber': ['streetnumber', 'StreetNumber', 'numero'],
                'address_unit': ['address_unit', 'AddressUnit', 'Address_Unit', 'Address Unit'],
                'postalcode': ['postalcode', 'PostalCode', 'postal_code', 'cp'],
                'city': ['city', 'City', 'ciudad'],
                'phone': ['phone', 'Phone', 'telefono'],
                'email': ['email', 'Email', 'correo'],
                'file': ['file', 'File', 'foto', 'imagen']
            }
            
            for key, posibles_nombres in campos_map.items():
                value = None
                for nombre in posibles_nombres:
                    if nombre in datos_personales.index:
                        value = datos_personales[nombre]
                        break
                
                if value is not None and pd.notna(value):
                    # Convertir a tipos nativos de Python
                    if isinstance(value, (np.integer,)):
                        value = int(value)
                    elif isinstance(value, (np.floating,)):
                        value = float(value)
                    response["datos_personales"][key] = str(value) if not isinstance(value, (int, float)) else value
                else:
                    response["datos_personales"][key] = "" if key != 'age' else None
        else:
            response["datos_personales"] = None
    else:
        response["datos_personales"] = None
    
    return response


@app.get("/estadisticas", tags=["Estadísticas Globales"])
def obtener_estadisticas():
    if df_limpio is None or df_limpio.empty:
        raise HTTPException(status_code=503, detail="Dataset no disponible")
    
    try:
        avg_income = df_limpio['Annual_Income'].mean()
        avg_debt = df_limpio['Outstanding_Debt'].mean()
        
        score_counts = {}
        if 'Credit_Score' in df_limpio.columns:
            score_counts = df_limpio['Credit_Score'].value_counts().to_dict()
        
        return {
            "total_registros": len(df_limpio),
            "ingreso_anual_promedio": round(float(avg_income), 2),
            "deuda_pendiente_promedio": round(float(avg_debt), 2),
            "distribucion_scores": score_counts,
            "dti_promedio": round(float(avg_debt / avg_income) if avg_income else 0, 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular estadísticas: {str(e)}")
