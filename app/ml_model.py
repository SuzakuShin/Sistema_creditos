# Nuevo archivo: app/ml_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class CreditRiskModel:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'credit_risk_model.pkl')
    
    def train(self, df):
        # Preparar features
        df['monthly_income'] = df['Annual_Income'] / 12
        df['debt_to_income'] = df['Outstanding_Debt'] / df['Annual_Income']
        
        # Codificar variables categóricas
        df['credit_score_encoded'] = self.label_encoder.fit_transform(df['Credit_Score'])
        
        # Crear target basado en reglas (para entrenamiento supervisado)
        df['risk_level'] = df.apply(self._assign_risk_label, axis=1)
        
        # Features para el modelo
        features = ['Annual_Income', 'Outstanding_Debt', 'monthly_income', 
                   'debt_to_income', 'credit_score_encoded']
        X = df[features]
        y = df['risk_level']
        
        # Split y entrenamiento
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Guardar modelo
        joblib.dump((self.model, self.label_encoder), self.model_path)
        
        accuracy = self.model.score(X_test, y_test)
        return accuracy
    
    def _assign_risk_label(self, row):
        # Misma lógica que tu agente experto pero para etiquetar datos
        dti = row['Outstanding_Debt'] / row['Annual_Income'] if row['Annual_Income'] > 0 else 1
        credit_score = row['Credit_Score']
        
        if dti < 0.1 and credit_score == 'Good':
            return 0  # Bajo riesgo
        elif dti < 0.3 and credit_score in ['Good', 'Standard']:
            return 1  # Medio riesgo
        else:
            return 2  # Alto riesgo
    
    def predict(self, cliente_data):
        if self.model is None:
            # Cargar modelo si existe
            if os.path.exists(self.model_path):
                self.model, self.label_encoder = joblib.load(self.model_path)
            else:
                return None
        
        # Preparar datos para predicción
        features = pd.DataFrame([cliente_data])
        features['credit_score_encoded'] = self.label_encoder.transform([cliente_data['Credit_Score']])
        
        prediction = self.model.predict(features[['Annual_Income', 'Outstanding_Debt', 
                                                  'monthly_income', 'debt_to_income', 
                                                  'credit_score_encoded']])
        return prediction[0]