import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


class CreditRiskModel:
    
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'credit_risk_model.pkl')
        self.feature_cols = []
        self._load_model()
    
    def _load_model(self):
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
        df = pd.DataFrame([data])
        
        if 'Credit_Score' in df.columns:
            try:
                df['credit_score_encoded'] = self.label_encoder.transform(df['Credit_Score'])
            except:
                score_map = {'Good': 2, 'Standard': 1, 'Poor': 0}
                df['credit_score_encoded'] = df['Credit_Score'].map(score_map).fillna(1)
        else:
            df['credit_score_encoded'] = 1
        default_values = {
            'Annual_Income': 0,
            'Outstanding_Debt': 0,
            'monthly_income': 0,
            'debt_to_income': 0,
            'loan_int_rate': 10,
            'person_emp_length': 0,
            'cb_person_cred_hist_length': 0,
            'credit_score_encoded': 1,
            'home_ownership_encoded': 0,
            'default_on_file': 0,
            'delayed_payments': 0
        }
        
        for col, default in default_values.items():
            if col not in df.columns:
                df[col] = default
        
        if self.feature_cols:
            cols_to_use = self.feature_cols
        else:
            cols_to_use = [
                'Annual_Income', 'Outstanding_Debt', 'monthly_income',
                'debt_to_income', 'credit_score_encoded', 'delayed_payments'
            ]
        
        for col in cols_to_use:
            if col not in df.columns:
                df[col] = 0
        
        return df[cols_to_use]
    
    def predict(self, data: dict):
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
    
    def predict_proba(self, data: dict):
        if self.model is None:
            return None
        
        try:
            features = self._prepare_features(data)
            proba = self.model.predict_proba(features)
            return proba[0].tolist()
        except Exception as e:
            print(f"❌ Error en predict_proba: {e}")
            return None
    
    def train(self, df: pd.DataFrame, force: bool = False):
        print("=" * 50)
        print(" ENTRENANDO MODELO DE MACHINE LEARNING (Scorecard)")
        print("=" * 50)
        
        df = df.copy()
        
        print("\n📊 Preparando features...")
        df['monthly_income'] = df['Annual_Income'] / 12.0
        df['debt_to_income'] = np.where(
            df['Annual_Income'] > 0,
            df['Outstanding_Debt'] / df['Annual_Income'],
            1.0
        )
        
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
        
        df['Credit_Score'] = df['Credit_Score'].fillna('Standard')
        valid_scores = ['Good', 'Standard', 'Poor']
        df = df[df['Credit_Score'].isin(valid_scores)]
        
        print("🏷️ Codificando variables...")
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(['Poor', 'Standard', 'Good'])
        df['credit_score_encoded'] = self.label_encoder.transform(df['Credit_Score'])
        
        print("🎯 Creando variable target (scorecard multicriterio)...")
        dti_max = df['debt_to_income'].max()
        df['score_dti'] = (1 - df['debt_to_income'] / dti_max) * 30
        score_map_puntos = {'Good': 40, 'Standard': 25, 'Poor': 5}
        df['score_credit'] = df['Credit_Score'].map(score_map_puntos)
        df['score_pagos'] = (1 - df['delayed_payments'] / 20) * 30
        df['puntaje_total'] = df['score_dti'] + df['score_credit'] + df['score_pagos']
        
        def classify(puntaje):
            if puntaje >= 65:
                return 0
            elif puntaje >= 35:
                return 1
            else:
                return 2
        
        df['risk_level'] = df['puntaje_total'].apply(classify)
        
        print("\n📊 Distribución de riesgo (target):")
        dist = df['risk_level'].value_counts().sort_index()
        for level, count in dist.items():
            labels = {0: 'Bajo', 1: 'Medio', 2: 'Alto'}
            print(f"   {labels[level]}: {count} ({count/len(df)*100:.1f}%)")
        
        self.feature_cols = [
            'Annual_Income', 'Outstanding_Debt', 'monthly_income',
            'debt_to_income', 'credit_score_encoded', 'delayed_payments'
        ]
        
        X = df[self.feature_cols].fillna(0)
        y = df['risk_level']
        
        print("\n🔄 Dividiendo datos (80% train / 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")
        
        print("\n Entrenando Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=10,
            min_samples_leaf=5, random_state=42, n_jobs=-1, class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        train_acc = self.model.score(X_train, y_train)
        test_acc = self.model.score(X_test, y_test)
        
        print(f"\n📈 Fidelidad al scorecard (Train): {train_acc:.2%}")
        print(f"   Fidelidad al scorecard (Test):  {test_acc:.2%}")
        print(f"\n💾 Guardando modelo...")
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump((self.model, self.label_encoder, self.feature_cols), self.model_path)
        print(f"✅ Modelo guardado en: {self.model_path}")
        
        return test_acc

    def train_with_real_target(self, df: pd.DataFrame, force: bool = False):
        print("=" * 50)
        print(" ENTRENANDO MODELO ML - Credit Risk Dataset")
        print("=" * 50)
        
        df = df.copy()
        
        required_cols = ['person_income', 'loan_amnt', 'loan_int_rate',
                         'loan_status', 'person_age', 'loan_percent_income',
                         'cb_person_cred_hist_length', 'person_emp_length']
        
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Faltan columnas: {missing}")
        
        print(f"\n📊 Datos cargados: {len(df):,} registros")
        
        print("\n🧹 Limpiando datos...")
        initial_rows = len(df)
        df = df.dropna(subset=['loan_status', 'person_income', 'loan_amnt'])
        df = df[df['person_age'].between(18, 100)]
        df = df[df['person_emp_length'].between(0, 60)]
        income_99 = df['person_income'].quantile(0.99)
        df = df[df['person_income'] <= income_99]
        print(f"   Registros eliminados: {initial_rows - len(df):,}")
        print(f"   Registros finales: {len(df):,}")
        
        print("\n📊 Creando features...")
        df['Annual_Income'] = df['person_income']
        df['Outstanding_Debt'] = df['loan_amnt']
        df['monthly_income'] = df['person_income'] / 12.0
        df['debt_to_income'] = df['loan_percent_income'] / 100.0
        
        np.random.seed(42)
        df['delayed_payments'] = np.where(
            df['cb_person_default_on_file'] == 'Y',
            np.random.randint(3, 10, len(df)),
            np.random.randint(0, 2, len(df))
        )
        
        grade_to_score = {
            'A': 'Good', 'B': 'Good', 'C': 'Standard',
            'D': 'Standard', 'E': 'Poor', 'F': 'Poor', 'G': 'Poor'
        }
        df['Credit_Score'] = df['loan_grade'].map(grade_to_score).fillna('Standard')
        
        df['person_emp_length'] = df['person_emp_length'].fillna(0)
        df['cb_person_cred_hist_length'] = df['cb_person_cred_hist_length'].fillna(0)
        
        print("\n📊 Estadísticas del target (loan_status):")
        target_counts = df['loan_status'].value_counts().sort_index()
        for val, count in target_counts.items():
            label = 'Pagó ✅' if val == 0 else 'No Pagó ❌'
            print(f"   {label}: {count:,} ({count/len(df)*100:.1f}%)")
        
        print("\n🏷️ Codificando variables...")
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(['Poor', 'Standard', 'Good'])
        df['credit_score_encoded'] = self.label_encoder.transform(df['Credit_Score'])
        
        df['home_ownership_encoded'] = df['person_home_ownership'].map({
            'OWN': 3, 'MORTGAGE': 2, 'RENT': 1, 'OTHER': 0
        }).fillna(0)
        
        df['default_on_file'] = np.where(df['cb_person_default_on_file'] == 'Y', 1, 0)
        
        self.feature_cols = [
            'Annual_Income', 'Outstanding_Debt', 'monthly_income',
            'debt_to_income', 'loan_int_rate', 'person_emp_length',
            'cb_person_cred_hist_length', 'credit_score_encoded',
            'home_ownership_encoded', 'default_on_file', 'delayed_payments'
        ]
        
        X = df[self.feature_cols].fillna(0)
        y = df['loan_status']
        
        print("\n Dividiendo datos (80% train / 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")
        
        print("\n Entrenando Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=150, max_depth=12, min_samples_split=20,
            min_samples_leaf=10, random_state=42, n_jobs=-1, class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        print("\n📈 Evaluando modelo...")
        train_acc = self.model.score(X_train, y_train)
        test_acc = self.model.score(X_test, y_test)
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_proba)
        
        print(f"   Accuracy Train: {train_acc:.2%}")
        print(f"   Accuracy Test:  {test_acc:.2%}")
        print(f"   ROC AUC:        {auc:.4f}")
        
        print("\n📋 Reporte de clasificación (Test):")
        print(classification_report(y_test, y_pred, target_names=['Pagó ✅', 'No Pagó ❌']))
        print("\n📊 Importancia de features:")
        importances = self.model.feature_importances_
        feature_importance = sorted(zip(self.feature_cols, importances), key=lambda x: x[1], reverse=True)
        for col, imp in feature_importance:
            bar = "█" * int(imp * 50)
            print(f"   {col:<30s}: {imp*100:5.1f}% {bar}")
        
        print(f"\n💾 Guardando modelo...")
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump((self.model, self.label_encoder, self.feature_cols), self.model_path)
        print(f"✅ Modelo guardado en: {self.model_path}")
        
        print("\n" + "=" * 50)
        print(f"🎯 ENTRENAMIENTO COMPLETADO")
        print(f"   Accuracy: {test_acc:.2%}")
        print(f"   ROC AUC:  {auc:.4f}")
        print("=" * 50)
        
        return test_acc


if __name__ == "__main__":
    print("\n🚀 INICIANDO ENTRENAMIENTO DEL MODELO ML\n")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    kaggle_path = os.path.join(current_dir, '..', 'data', 'credit_risk_dataset.csv')
    original_path = os.path.join(current_dir, '..', 'data', 'clientes_limpios.csv')
    
    if os.path.exists(kaggle_path):
        print(f"📂 Dataset Kaggle encontrado: {kaggle_path}")
        df = pd.read_csv(kaggle_path, low_memory=False)
        model = CreditRiskModel()
        model.train_with_real_target(df)
    elif os.path.exists(original_path):
        print(f"📂 Dataset original encontrado: {original_path}")
        df = pd.read_csv(original_path, low_memory=False)
        model = CreditRiskModel()
        model.train(df, force=True)
    else:
        print("❌ No se encontraron datasets para entrenar.")
        print(f"   Kaggle: {kaggle_path}")
        print(f"   Original: {original_path}")