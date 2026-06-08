"""
Modelo de Machine Learning para predicción de riesgo crediticio.
Entrenado con Credit Score Classification (Kaggle).
Aplica Hard Rules del Agente Experto (>5 atrasos = Rechazo).
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


class CreditRiskModel:
    """Modelo de Machine Learning para predicción de riesgo crediticio"""
    
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'credit_risk_model.pkl')
        self.feature_cols = []
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo entrenado si existe"""
        try:
            if os.path.exists(self.model_path):
                data = joblib.load(self.model_path)
                if len(data) == 3:
                    self.model, self.label_encoder, self.feature_cols = data
                else:
                    self.model, self.label_encoder = data
                    self.feature_cols = []
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
        
        # Codificar Credit_Mix
        if 'Credit_Mix' in df.columns:
            mix_map = {'Good': 2, 'Standard': 1, 'Bad': 0}
            df['credit_mix_encoded'] = df['Credit_Mix'].map(mix_map).fillna(1)
        else:
            df['credit_mix_encoded'] = 1
        
        # Codificar Payment_of_Min_Amount
        if 'Payment_of_Min_Amount' in df.columns:
            pay_map = {'Yes': 1, 'No': 0, 'NM': 0}
            df['payment_min_encoded'] = df['Payment_of_Min_Amount'].map(pay_map).fillna(0)
        else:
            df['payment_min_encoded'] = 0
        
        # Asegurar columnas necesarias
        default_values = {
            'Annual_Income': 0, 'Outstanding_Debt': 0,
            'monthly_income': 0, 'debt_to_income': 0,
            'Interest_Rate': 10, 'Num_of_Loan': 1,
            'Num_Credit_Card': 1, 'Num_Bank_Accounts': 1,
            'Credit_History_Age': 5, 'credit_score_encoded': 1,
            'credit_mix_encoded': 1, 'payment_min_encoded': 0,
            'delayed_payments': 0
        }
        
        for col, default in default_values.items():
            if col not in df.columns:
                df[col] = default
        
        # Usar feature_cols guardadas
        if self.feature_cols:
            cols_to_use = self.feature_cols
        else:
            cols_to_use = [
                'Annual_Income', 'Outstanding_Debt', 'monthly_income',
                'debt_to_income', 'Interest_Rate', 'Num_of_Loan',
                'credit_score_encoded', 'credit_mix_encoded',
                'payment_min_encoded', 'delayed_payments',
                'Credit_History_Age', 'Num_Credit_Card', 'Num_Bank_Accounts'
            ]
        
        for col in cols_to_use:
            if col not in df.columns:
                df[col] = 0
        
        return df[cols_to_use]
    
    def predict(self, data: dict):
        """
        Predice el nivel de riesgo.
        APLICA HARD RULE: >5 pagos atrasados = Riesgo Alto automático
        Retorna: 0 (Bajo), 1 (Medio), 2 (Alto) o None
        """
        # HARD RULE del Agente Experto
        delayed = data.get('delayed_payments', 0)
        if delayed > 5:
            return 2  # Riesgo Alto
        
        if self.model is None:
            return None
        
        try:
            features = self._prepare_features(data)
            prediction = self.model.predict(features)
            return int(prediction[0])
        except Exception as e:
            print(f"❌ Error en predicción ML: {e}")
            return None
    
    def predict_proba(self, data: dict):
        """Devuelve probabilidades de cada clase"""
        delayed = data.get('delayed_payments', 0)
        if delayed > 5:
            return [0.0, 0.0, 1.0]
        
        if self.model is None:
            return None
        
        try:
            features = self._prepare_features(data)
            proba = self.model.predict_proba(features)
            return proba[0].tolist()
        except Exception as e:
            print(f"❌ Error en predict_proba: {e}")
            return None
    
    # ================================================================
    # ENTRENAMIENTO CON CREDIT SCORE CLASSIFICATION (KAGGLE)
    # ================================================================
    def train(self, df: pd.DataFrame, force: bool = False):
        """
        Entrena el modelo con Credit Score Classification (Kaggle).
        Aplica la misma lógica del Agente Experto:
          - Scorecard idéntico para el target
          - Hard Rule: >5 pagos atrasados = Riesgo Alto
        """
        print("=" * 60)
        print("🔄 ENTRENANDO MODELO ML - Credit Score Classification")
        print("=" * 60)
        
        df = df.copy()
        
        print(f"\n📊 Datos cargados: {len(df):,} registros")
        
        # ============================================================
        # LIMPIEZA
        # ============================================================
        print("\n🧹 Limpiando datos...")
        initial_rows = len(df)
        
        # Eliminar columnas irrelevantes
        cols_to_drop = ['ID', 'Customer_ID', 'Name', 'SSN', 'Month',
                       'Occupation', 'Type_of_Loan', 'Changed_Credit_Limit',
                       'Num_Credit_Inquiries', 'Total_EMI_per_month',
                       'Amount_invested_monthly', 'Payment_Behaviour',
                       'Monthly_Balance']
        for col in cols_to_drop:
            if col in df.columns:
                df = df.drop(columns=[col])
        
        # Limpiar Credit_Score
        df['Credit_Score'] = df['Credit_Score'].fillna('Standard')
        valid_scores = ['Good', 'Standard', 'Poor']
        df = df[df['Credit_Score'].isin(valid_scores)]
        
        # Limpiar pagos atrasados
        if 'Num_of_Delayed_Payment' in df.columns:
            df['delayed_payments'] = pd.to_numeric(
                df['Num_of_Delayed_Payment'].astype(str).str.replace('_', '').str.strip(),
                errors='coerce'
            ).fillna(0).clip(lower=0, upper=20).astype(int)
        elif 'Delay_from_due_date' in df.columns:
            df['delayed_payments'] = pd.to_numeric(
                df['Delay_from_due_date'].astype(str).str.replace('_', '').str.strip(),
                errors='coerce'
            ).fillna(0).clip(lower=0, upper=20).astype(int)
        else:
            df['delayed_payments'] = 0
        
        # Limpiar valores numéricos
        for col in ['Annual_Income', 'Outstanding_Debt', 'Interest_Rate',
                   'Num_of_Loan', 'Num_Credit_Card', 'Num_Bank_Accounts',
                   'Credit_History_Age', 'Monthly_Inhand_Salary']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).clip(lower=0)
        
        # Eliminar outliers extremos
        df = df[df['Annual_Income'] < df['Annual_Income'].quantile(0.99)]
        df = df[df['Outstanding_Debt'] < df['Outstanding_Debt'].quantile(0.99)]
        
        print(f"   Registros después de limpieza: {len(df):,}")
        print(f"   Pagos atrasados - Max: {df['delayed_payments'].max()}, Media: {df['delayed_payments'].mean():.1f}")
        
        # ============================================================
        # FEATURE ENGINEERING
        # ============================================================
        print("\n📊 Creando features...")
        
        df['monthly_income'] = df['Annual_Income'] / 12.0
        df['debt_to_income'] = np.where(
            df['Annual_Income'] > 0,
            df['Outstanding_Debt'] / df['Annual_Income'],
            1.0
        )
        
        # Codificar variables categóricas
        print("🏷️ Codificando variables...")
        
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(['Poor', 'Standard', 'Good'])
        df['credit_score_encoded'] = self.label_encoder.transform(df['Credit_Score'])
        
        if 'Credit_Mix' in df.columns:
            mix_map = {'Good': 2, 'Standard': 1, 'Bad': 0}
            df['credit_mix_encoded'] = df['Credit_Mix'].map(mix_map).fillna(1).astype(int)
        else:
            df['credit_mix_encoded'] = 1
        
        if 'Payment_of_Min_Amount' in df.columns:
            pay_map = {'Yes': 1, 'No': 0, 'NM': 0}
            df['payment_min_encoded'] = df['Payment_of_Min_Amount'].map(pay_map).fillna(0).astype(int)
        else:
            df['payment_min_encoded'] = 0
        
        # ============================================================
        # TARGET: Misma lógica que el Agente Experto
        # ============================================================
        print("\n🎯 Creando target (scorecard del Agente Experto)...")
        
        def assign_risk(row):
            delayed = row.get('delayed_payments', 0)
            
            # HARD RULE: >5 atrasos = RECHAZO AUTOMÁTICO
            if delayed > 5:
                return 2  # Alto
            
            dti = row['debt_to_income']
            score = row['Credit_Score']
            
            puntaje = 0
            
            # DTI (25 pts) - idéntico al agente
            if dti < 0.10:
                puntaje += 25
            elif dti < 0.20:
                puntaje += 18
            elif dti < 0.30:
                puntaje += 10
            elif dti < 0.40:
                puntaje += 4
            
            # Credit Score (35 pts) - idéntico al agente
            if score == 'Good':
                puntaje += 35
            elif score == 'Standard':
                puntaje += 18
            
            # Pagos Atrasados (40 pts) - idéntico al agente
            if delayed == 0:
                puntaje += 40
            elif delayed == 1:
                puntaje += 25
            elif delayed == 2:
                puntaje += 12
            elif delayed <= 5:
                puntaje += 3
            
            # Clasificación - idéntica al agente
            if puntaje >= 75:
                return 0  # Bajo
            elif puntaje >= 45:
                return 1  # Medio
            else:
                return 2  # Alto
        
        df['risk_level'] = df.apply(assign_risk, axis=1)
        
        print("\n📊 Distribución de riesgo (target):")
        dist = df['risk_level'].value_counts().sort_index()
        for level, count in dist.items():
            labels = {0: 'Bajo', 1: 'Medio', 2: 'Alto'}
            pct = count/len(df)*100
            print(f"   {labels[level]}: {count:,} ({pct:.1f}%)")
        
        # ============================================================
        # FEATURES FINALES
        # ============================================================
        self.feature_cols = [
            'Annual_Income', 'Outstanding_Debt', 'monthly_income',
            'debt_to_income', 'Interest_Rate', 'Num_of_Loan',
            'Num_Credit_Card', 'Num_Bank_Accounts',
            'Credit_History_Age', 'credit_score_encoded',
            'credit_mix_encoded', 'payment_min_encoded',
            'delayed_payments'
        ]
        
        X = df[self.feature_cols].fillna(0)
        y = df['risk_level']
        
        # ============================================================
        # CORRELACIONES
        # ============================================================
        print("\n📊 Correlación features vs target:")
        for col in self.feature_cols:
            if col in df.columns:
                corr = df[col].corr(df['risk_level'])
                print(f"   {col:<30s}: {corr:+.4f}")
        
        # ============================================================
        # TRAIN/TEST SPLIT
        # ============================================================
        print("\n🔄 Dividiendo datos (80% train / 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")
        
        # ============================================================
        # ENTRENAR
        # ============================================================
        print("\n🌲 Entrenando Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        # ============================================================
        # EVALUAR
        # ============================================================
        print("\n📈 Evaluando modelo...")
        train_acc = self.model.score(X_train, y_train)
        test_acc = self.model.score(X_test, y_test)
        y_pred = self.model.predict(X_test)
        
        print(f"   Accuracy Train: {train_acc:.2%}")
        print(f"   Accuracy Test:  {test_acc:.2%}")
        
        print("\n📋 Reporte de clasificación (Test):")
        print(classification_report(y_test, y_pred,
                                    target_names=['Bajo', 'Medio', 'Alto']))
        
        # ============================================================
        # FEATURE IMPORTANCE
        # ============================================================
        print("\n📊 Importancia de features:")
        importances = self.model.feature_importances_
        feature_importance = sorted(zip(self.feature_cols, importances),
                                   key=lambda x: x[1], reverse=True)
        
        for col, imp in feature_importance:
            bar = "█" * int(imp * 50)
            print(f"   {col:<30s}: {imp*100:5.1f}% {bar}")
        
        # ============================================================
        # GUARDAR
        # ============================================================
        print(f"\n💾 Guardando modelo...")
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump((self.model, self.label_encoder, self.feature_cols), self.model_path)
        print(f"✅ Modelo guardado en: {self.model_path}")
        
        print("\n" + "=" * 60)
        print(f"🎯 ENTRENAMIENTO COMPLETADO - Accuracy: {test_acc:.2%}")
        print("=" * 60)
        
        return test_acc


# ============================================================
# SCRIPT DE ENTRENAMIENTO
# ============================================================
if __name__ == "__main__":
    print("\n🚀 INICIANDO ENTRENAMIENTO DEL MODELO ML\n")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(current_dir, '..', 'data', 'train.csv')
    
    if os.path.exists(train_path):
        print(f"📂 Dataset Kaggle encontrado: {train_path}")
        df = pd.read_csv(train_path, low_memory=False)
        model = CreditRiskModel()
        model.train(df, force=True)
    else:
        print(f"❌ No se encontró el dataset: {train_path}")
        print("   Descargalo de: https://www.kaggle.com/datasets/parisrohan/credit-score-classification")
        print("   Guardalo como: data/train.csv")