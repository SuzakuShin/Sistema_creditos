import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from .schemas import ClienteEval, DecisionResponse
from .agent import evaluar_cliente

df_limpio = None
df_personal = None

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

    if df_limpio is None or df_limpio.empty:
        raise HTTPException(status_code=503, detail="Dataset crediticio no disponible. Ejecute data_cleaner.py primero.")
    
    cliente_credito = None
    if 'Customer_ID' in df_limpio.columns:
        cliente_credito = df_limpio[df_limpio['Customer_ID'] == cliente_id]
    
    if (cliente_credito is None or cliente_credito.empty) and 'ID' in df_limpio.columns:
        cliente_credito = df_limpio[df_limpio['ID'] == cliente_id]
    
    if cliente_credito is None or cliente_credito.empty:
        raise HTTPException(status_code=404, detail=f"Cliente '{cliente_id}' no encontrado en datos crediticios")
    
    datos_credito = cliente_credito.iloc[0]    
    pagos_atrasados = 0
    if 'Num_of_Delayed_Payment' in datos_credito.index:
        try:
            pagos_atrasados = int(float(datos_credito['Num_of_Delayed_Payment']))
        except:
            pagos_atrasados = 0
    
    try:
        decision = evaluar_cliente(
            ingreso_anual=float(datos_credito['Annual_Income']),
            deuda_pendiente=float(datos_credito['Outstanding_Debt']),
            credit_score=str(datos_credito['Credit_Score']),
            pagos_atrasados=pagos_atrasados
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al evaluar cliente: {str(e)}")
    
    response = {
        "Customer_ID": cliente_id,
        "datos_crediticios": {
            "ingreso_anual": float(datos_credito.get('Annual_Income', 0)),
            "deuda_pendiente": float(datos_credito.get('Outstanding_Debt', 0)),
            "credit_score": str(datos_credito.get('Credit_Score', 'Standard')),
            "pagos_atrasados": pagos_atrasados,
            "dti": float(datos_credito.get('DTI', 0)) if 'DTI' in datos_credito.index else 0
        },
        "decision_agente": decision
    }
    
    if df_personal is not None and not df_personal.empty:
        cliente_personal = None
        
        for col in ['person_id', 'Person_ID', 'Customer_ID', 'ID']:
            if col in df_personal.columns:
                cliente_personal = df_personal[df_personal[col] == cliente_id]
                if not cliente_personal.empty:
                    break
        
        if cliente_personal is not None and not cliente_personal.empty:
            datos_personales = cliente_personal.iloc[0]
            response["datos_personales"] = {}
            
            campos_map = {
                'firstname': ['firstname', 'FirstName', 'first_name', 'nombre'],
                'lastname': ['lastname', 'LastName', 'last_name', 'apellido'],
                'gender': ['gender', 'Gender', 'sexo'],
                'age': ['age', 'Age', 'edad'],
                'street': ['street', 'Street', 'calle'],
                'streetnumber': ['streetnumber', 'StreetNumber', 'numero'],
                'address_unit': ['address_unit', 'AddressUnit', 'Address_Unit'],
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
                    response["datos_personales"][key] = str(value)
                else:
                    response["datos_personales"][key] = ""
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