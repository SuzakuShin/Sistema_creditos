import pandas as pd
import numpy as np
import os
import re

def clean_numeric_value(val):
    if pd.isna(val):
        return np.nan
    
    val_str = str(val).strip()
    
   
    if val_str == '' or val_str == '_':
        return np.nan

    cleaned = re.sub(r'[^\d.-]', '', val_str)
    
    if cleaned == '' or cleaned == '.' or cleaned == '-':
        return np.nan
    

    point_count = cleaned.count('.')
    
    try:
        if point_count > 1:
            parts = cleaned.split('.')
            integer_part = ''.join(parts[:-1])
            decimal_part = parts[-1]
            if len(decimal_part) > 2:
                cleaned = ''.join(parts)
            else:
                cleaned = f"{integer_part}.{decimal_part}"
        
        return float(cleaned)
    except (ValueError, TypeError):
        return np.nan

def clean_text_value(val):
    if pd.isna(val):
        return np.nan
    
    val_str = str(val).strip()
    
    # Si contiene caracteres claramente basura
    if any(char in val_str for char in ['!', '@', '#', '$', '%', '^', '&', '*']):
        return np.nan
    
    # Si es solo underscores
    if val_str.replace('_', '').strip() == '':
        return np.nan
    
    return val_str

def clean_data(input_path: str, output_path: str):
    print(f"📂 Cargando datos desde {input_path}...")
    df = pd.read_csv(input_path, low_memory=False)
    
    print(f"📊 Dimensiones originales: {df.shape}")
    print(f"📋 Columnas encontradas: {list(df.columns)}")
    
    # 1. Eliminar duplicados exactos
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"🗑️  Duplicados eliminados: {initial_rows - len(df)}")
    
    # 2. Limpiar columnas numéricas principales
    print("\n🧹 Limpiando columnas numéricas...")
    
    numeric_columns = [
        'Annual_Income', 
        'Outstanding_Debt', 
        'Monthly_Inhand_Salary',
        'Interest_Rate',
        'Num_of_Loan',
        'Num_of_Delayed_Payment',
        'Changed_Credit_Limit',
        'Num_Credit_Inquiries',
        'Amount_invested_monthly',
        'Monthly_Balance',
        'Total_EMI_per_month',
        'Age',
        'Num_Bank_Accounts',
        'Num_Credit_Card',
        'Delay_from_due_date'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            before_nulls = df[col].isna().sum()
            df[col] = df[col].apply(clean_numeric_value)
            after_nulls = df[col].isna().sum()
            print(f"  ✓ {col}: {before_nulls} -> {after_nulls} nulos")
    
   
    print("\n🧹 Limpiando columnas de texto...")
    
    text_columns = ['Name', 'Occupation', 'Credit_Score', 'Credit_Mix', 'Payment_Behaviour', 'Month', 'Type_of_Loan']
    
    for col in text_columns:
        if col in df.columns:
            before_nulls = df[col].isna().sum()
            df[col] = df[col].apply(clean_text_value)
            after_nulls = df[col].isna().sum()
            print(f"  ✓ {col}: {before_nulls} -> {after_nulls} nulos")
    
   
    print("\n🔧 Corrigiendo valores inválidos...")
    
    positive_columns = ['Annual_Income', 'Age', 'Num_Bank_Accounts', 'Num_Credit_Card']
    
    for col in positive_columns:
        if col in df.columns:
           
            if not pd.api.types.is_numeric_dtype(df[col]):
                print(f"  ⚠️ {col}: No es numérica, intentando convertir...")
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
           
            try:
                neg_count = (df[col] < 0).sum()
                if neg_count > 0:
                    df.loc[df[col] < 0, col] = np.nan
                    print(f"  ✓ {col}: {neg_count} valores negativos -> NaN")
                else:
                    print(f"  ✓ {col}: Sin valores negativos")
            except Exception as e:
                print(f"  ⚠️ {col}: Error al verificar: {e}")
    
   
    if 'Credit_Score' in df.columns:
        valid_scores = ['Good', 'Standard', 'Poor']
        invalid_count = 0
        for idx, val in df['Credit_Score'].items():
            if pd.notna(val) and str(val) not in valid_scores:
                df.at[idx, 'Credit_Score'] = np.nan
                invalid_count += 1
        if invalid_count > 0:
            print(f"  ✓ Credit_Score: {invalid_count} valores inválidos -> NaN")
    
   
    print("\n📊 Rellenando valores nulos...")
     
    for col in numeric_columns:
        if col in df.columns and df[col].isna().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                median_val = df[col].median()
                if pd.isna(median_val):
                    median_val = 0
                df[col] = df[col].fillna(median_val)
                print(f"  ✓ {col}: rellenado con mediana ({median_val:.2f})")
    
    # Para Credit_Score, usar la moda
    if 'Credit_Score' in df.columns:
        mode_val = df['Credit_Score'].mode()
        if not mode_val.empty:
            df['Credit_Score'] = df['Credit_Score'].fillna(mode_val[0])
            print(f"  ✓ Credit_Score: rellenado con moda ({mode_val[0]})")
        else:
            df['Credit_Score'] = df['Credit_Score'].fillna('Standard')
            print(f"  ✓ Credit_Score: rellenado con 'Standard'")
    
    # 7. Crear columnas calculadas
    print("\n📐 Creando columnas calculadas...")
    
    # Monthly_Income desde Annual_Income
    if 'Annual_Income' in df.columns:
        df['Monthly_Income'] = df['Annual_Income'] / 12.0
        print(f"  ✓ Monthly_Income calculado")
    
    # DTI (Debt to Income Ratio)
    if 'Outstanding_Debt' in df.columns and 'Annual_Income' in df.columns:
        df['DTI'] = np.where(
            df['Annual_Income'] > 0,
            df['Outstanding_Debt'] / df['Annual_Income'],
            1.0  # Si no hay ingreso, DTI = 100%
        )
        print(f"  ✓ DTI calculado")
        print(f"    DTI promedio: {df['DTI'].mean():.4f}")
        print(f"    DTI mediana: {df['DTI'].median():.4f}")
    
    # 8. Estadísticas finales
    print(f"\n📊 Dimensiones finales: {df.shape}")
    print(f"📊 Columnas finales: {list(df.columns)}")
    
    # Mostrar resumen de datos limpios
    print("\n📈 Resumen de datos limpios:")
    if 'Annual_Income' in df.columns:
        print(f"  Ingreso anual - Min: ${df['Annual_Income'].min():,.2f}, Max: ${df['Annual_Income'].max():,.2f}, Promedio: ${df['Annual_Income'].mean():,.2f}")
    if 'Outstanding_Debt' in df.columns:
        print(f"  Deuda - Min: ${df['Outstanding_Debt'].min():,.2f}, Max: ${df['Outstanding_Debt'].max():,.2f}, Promedio: ${df['Outstanding_Debt'].mean():,.2f}")
    if 'Credit_Score' in df.columns:
        print(f"  Distribución Credit Score:")
        print(df['Credit_Score'].value_counts().to_string())
    
    # 9. Guardar datos limpios
    print(f"\n💾 Guardando datos limpios en {output_path}...")
    df.to_csv(output_path, index=False)
    print("✅ ¡Limpieza completada exitosamente!")
    
    return df

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(current_dir, "..", "data", "train.csv")
    output_csv = os.path.join(current_dir, "..", "data", "train_processed.csv")
    
    # Verificar que el archivo de entrada existe
    if not os.path.exists(input_csv):
        print(f"❌ Error: No se encuentra el archivo {input_csv}")
        print("Asegúrate de que el dataset esté en la carpeta 'data' con el nombre 'clientes.csv'")
    else:
        clean_data(input_csv, output_csv)