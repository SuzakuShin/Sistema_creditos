"""
Modelo de Machine Learning para predicción de riesgo crediticio
Entrena un Random Forest y guarda el modelo para uso en la API.
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


class CreditRiskModel:
    """Modelo de Machine Learning para predicción de riesgo crediticio"""
    
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'credit_risk_model.pkl')
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo entrenado si existe"""
        try:
            if os.path.exists(self.model_path):
                self.model, self.label_encoder = joblib.load(self.model_path)
                print(f"✅ Modelo ML cargado desde {self.model_path}")
            else:
                print(f"⚠️ Modelo ML no encontrado en {self.model_path}")
        except Exception as e:
            print(f"⚠️ Error al cargar modelo ML: {e}")
    
    def _prepare_features(self, data: dict):
        """Prepara las features para el modelo"""
        df = pd.DataFrame([data])
        
        # Codificar Credit_Score
        if 'Credit_Score' in df.columns:
            try:
                df['credit_score_encoded'] = self.label_encoder.transform(df['Credit_Score'])
            except:
                score_map = {'Good': 2, 'Standard': 1, 'Poor': 0}
                df['credit_score_encoded'] = df['Credit_Score'].map(score_map).fillna(1)
        else:
            df['credit_score_encoded'] = 1
        
        if 'delayed_payments' not in df.columns:
            df['delayed_payments'] = 0
        
        feature_cols = [
            'Annual_Income', 
            'Outstanding_Debt', 
            'monthly_income', 
            'debt_to_income', 
            'credit_score_encoded',
            'delayed_payments'     
        ]
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0
        
        return df[feature_cols]
    
    def predict(self, data: dict):
        """
        Predice el nivel de riesgo para un cliente
        Retorna: 0 (Bajo), 1 (Medio), 2 (Alto) o None
        """
        if self.model is None:
            print("⚠️ Modelo no cargado")
            return None
        
        try:
            features = self._prepare_features(data)
            prediction = self.model.predict(features)
            return int(prediction[0])
        except Exception as e:
            print(f"❌ Error en predicción ML: {e}")
            return None
    
    
    def train(self, df: pd.DataFrame, force: bool = False):
        """
        Entrena el modelo con datos históricos
        
        Args:
            df: DataFrame con datos de clientes
            force: Si es True, reentrena aunque ya exista modelo
        """
        print("=" * 50)
        print("🔄 ENTRENANDO MODELO DE MACHINE LEARNING")
        print("=" * 50)
        
        df = df.copy()
        
        # Calcular features derivadas
        print("\n📊 Preparando features...")
        df['monthly_income'] = df['Annual_Income'] / 12.0
        df['debt_to_income'] = np.where(
            df['Annual_Income'] > 0,
            df['Outstanding_Debt'] / df['Annual_Income'],
            1.0
        )
        
        # Procesar pagos atrasados
        print("🔧 Procesando pagos atrasados...")
        if 'Num_of_Delayed_Payment' in df.columns:
            df['delayed_payments'] = pd.to_numeric(
                df['Num_of_Delayed_Payment'].astype(str).str.replace('_', '').str.strip(),
                errors='coerce'
            )
        elif 'Delay_from_due_date' in df.columns:
            df['delayed_payments'] = pd.to_numeric(
                df['Delay_from_due_date'].astype(str).str.replace('_', '').str.strip(),
                errors='coerce'
            )
        else:
            df['delayed_payments'] = 0
        
        df['delayed_payments'] = df['delayed_payments'].fillna(0).clip(lower=0, upper=20)
        print(f"   Pagos atrasados - Min: {df['delayed_payments'].min():.0f}, "
            f"Max: {df['delayed_payments'].max():.0f}, "
            f"Media: {df['delayed_payments'].mean():.1f}")
        
        # Limpiar Credit_Score
        df['Credit_Score'] = df['Credit_Score'].fillna('Standard')
        valid_scores = ['Good', 'Standard', 'Poor']
        df = df[df['Credit_Score'].isin(valid_scores)]
        
        # Codificar Credit_Score
        print("🏷️ Codificando variables...")
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(['Poor', 'Standard', 'Good'])
        df['credit_score_encoded'] = self.label_encoder.transform(df['Credit_Score'])
        
        # ================================================================
        # NUEVO TARGET: Scorecard simplificado que usa TODAS las variables
        # pero de forma que ninguna variable por sí sola pueda predecirlo
        # ================================================================
        print("🎯 Creando variable target (scorecard multicriterio)...")
        
        # Normalizar DTI a escala 0-1 (invertido: menor DTI = mejor)
        dti_max = df['debt_to_income'].max()
        df['score_dti'] = (1 - df['debt_to_income'] / dti_max) * 30
        
        # Score crediticio a puntos
        score_map_puntos = {'Good': 40, 'Standard': 25, 'Poor': 5}
        df['score_credit'] = df['Credit_Score'].map(score_map_puntos)
        
        # Pagos atrasados a puntos (invertido: menos atrasos = mejor)
        df['score_pagos'] = (1 - df['delayed_payments'] / 20) * 30
        
        # Puntaje total (0-100)
        df['puntaje_total'] = df['score_dti'] + df['score_credit'] + df['score_pagos']
        
        # Clasificación final con umbrales que generan overlap
        def classify(puntaje):
            if puntaje >= 65:
                return 0  # Bajo
            elif puntaje >= 35:
                return 1  # Medio
            else:
                return 2  # Alto
        
        df['risk_level'] = df['puntaje_total'].apply(classify)
        
        # Mostrar distribución
        print("\n📊 Distribución de riesgo (target):")
        dist = df['risk_level'].value_counts().sort_index()
        for level, count in dist.items():
            labels = {0: 'Bajo', 1: 'Medio', 2: 'Alto'}
            print(f"   {labels[level]}: {count} ({count/len(df)*100:.1f}%)")
        
        # Mostrar estadísticas del puntaje
        print(f"\n📊 Estadísticas del puntaje total:")
        print(f"   Min: {df['puntaje_total'].min():.1f} | Max: {df['puntaje_total'].max():.1f}")
        print(f"   Media: {df['puntaje_total'].mean():.1f} | Mediana: {df['puntaje_total'].median():.1f}")
        
        # FEATURES (las mismas, pero ahora el target es más complejo)
        feature_cols = [
            'Annual_Income', 
            'Outstanding_Debt', 
            'monthly_income', 
            'debt_to_income', 
            'credit_score_encoded',
            'delayed_payments'
        ]
        
        X = df[feature_cols].fillna(0)
        y = df['risk_level']
        
        # Split train/test
        print("\n🔄 Dividiendo datos (80% train / 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   Train: {len(X_train)} | Test: {len(X_test)}")
        
        # Entrenar modelo (reducir max_depth para evitar overfitting)
        print("\n🌲 Entrenando Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,            # Reducido de 15 a 10
            min_samples_split=10,    # Aumentado de 5 a 10
            min_samples_leaf=5,      # Aumentado de 2 a 5
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        # Evaluar
        print("\n📈 Evaluando modelo...")
        train_acc = self.model.score(X_train, y_train)
        test_acc = self.model.score(X_test, y_test)
        
        print(f"   Accuracy Train: {train_acc:.2%}")
        print(f"   Accuracy Test:  {test_acc:.2%}")
        
        # Reporte de clasificación
        from sklearn.metrics import classification_report
        y_pred = self.model.predict(X_test)
        print("\n📋 Reporte de clasificación (Test):")
        print(classification_report(y_test, y_pred, 
                                    target_names=['Bajo', 'Medio', 'Alto']))
        
        # Importancia de features
        print("\n📊 Importancia de features:")
        importances = self.model.feature_importances_
        
        feature_importance = sorted(
            zip(feature_cols, importances), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for col, imp in feature_importance:
            bar = "█" * int(imp * 50)
            print(f"   {col:<25s}: {imp:.4f} {bar}")
        
        # Guardar modelo
        print(f"\n💾 Guardando modelo...")
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump((self.model, self.label_encoder), self.model_path)
        print(f"✅ Modelo guardado en: {self.model_path}")
        
        print("\n" + "=" * 50)
        print(f"🎯 ENTRENAMIENTO COMPLETADO - Accuracy: {test_acc:.2%}")
        print("=" * 50)
        
        return test_acc


# ENTRENAMIENTO
if __name__ == "__main__":
    print("\n🚀 INICIANDO ENTRENAMIENTO DEL MODELO ML\n")
    
    # Buscar datos
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, '..', 'data', 'clientes_limpios.csv')
    
    print(f"📂 Buscando datos en: {data_path}")
    
    if os.path.exists(data_path):
        print(f"✅ Archivo encontrado")
        print(f"📊 Cargando datos...")
        
        try:
            df = pd.read_csv(data_path, low_memory=False)
            print(f"✅ Datos cargados: {len(df):,} registros")
            print(f"📋 Columnas: {list(df.columns)[:10]}...")
            
            # Entrenar modelo
            model = CreditRiskModel()
            accuracy = model.train(df, force=True)
            
            print(f"\n✅ Listo! El modelo está disponible para la API.")
            
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ No se encontró el archivo: {data_path}")
        print("Asegúrate de ejecutar primero: python -m app.data_cleaner")