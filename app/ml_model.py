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
        
        # Seleccionar features
        feature_cols = ['Annual_Income', 'Outstanding_Debt', 'monthly_income', 
                       'debt_to_income', 'credit_score_encoded']
        
        # Asegurar que todas las columnas existan
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
        
        # Crear copia para no modificar el original
        df = df.copy()
        
        # Calcular features derivadas
        print("\n📊 Preparando features...")
        df['monthly_income'] = df['Annual_Income'] / 12.0
        df['debt_to_income'] = np.where(
            df['Annual_Income'] > 0,
            df['Outstanding_Debt'] / df['Annual_Income'],
            1.0
        )
        
        # Limpiar Credit_Score
        df['Credit_Score'] = df['Credit_Score'].fillna('Standard')
        valid_scores = ['Good', 'Standard', 'Poor']
        df = df[df['Credit_Score'].isin(valid_scores)]
        
        # Codificar Credit_Score
        print("🏷️ Codificando variables...")
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(['Poor', 'Standard', 'Good'])  # Orden específico
        df['credit_score_encoded'] = self.label_encoder.transform(df['Credit_Score'])
        
        # Crear variable target basada en reglas
        print("🎯 Creando variable target...")
        def assign_risk(row):
            dti = row['debt_to_income']
            score = row['Credit_Score']
            delayed = row.get('Num_of_Delayed_Payment', 0)
            
            if pd.isna(delayed):
                delayed = 0
            
            # Dar más peso al DTI y Score que a los pagos atrasados
            # para balancear mejor las clases
            if dti < 0.2 and score == 'Good' and delayed <= 3:
                return 0  # Bajo
            elif dti < 0.4 and score in ['Good', 'Standard'] and delayed <= 5:
                return 1  # Medio
            else:
                return 2  # Alto
        
        df['risk_level'] = df.apply(assign_risk, axis=1)
        
        # Mostrar distribución
        print("\n📊 Distribución de riesgo:")
        dist = df['risk_level'].value_counts().sort_index()
        for level, count in dist.items():
            labels = {0: 'Bajo', 1: 'Medio', 2: 'Alto'}
            print(f"   {labels[level]}: {count} ({count/len(df)*100:.1f}%)")
        
        # Preparar features y target
        feature_cols = ['Annual_Income', 'Outstanding_Debt', 'monthly_income', 
                       'debt_to_income', 'credit_score_encoded']
        
        X = df[feature_cols].fillna(0)
        y = df['risk_level']
        
        # Split train/test
        print("\n🔄 Dividiendo datos (80% train / 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   Train: {len(X_train)} | Test: {len(X_test)}")
        
        # Entrenar modelo
        print("\n🌲 Entrenando Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
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
        
        # Importancia de features
        print("\n📊 Importancia de features:")
        importances = self.model.feature_importances_
        for col, imp in zip(feature_cols, importances):
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


# ============================================================
# SCRIPT DE ENTRENAMIENTO
# ============================================================
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