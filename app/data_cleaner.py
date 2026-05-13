import pandas as pd
import numpy as np
import os

def clean_data(input_path: str, output_path: str):
    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path, low_memory=False)
    
    print(f"Original shape: {df.shape}")
    
    # Drop exact duplicates
    df = df.drop_duplicates()
    
    # Helper to clean strings containing invalid characters
    def clean_numeric_str(val):
        if pd.isna(val):
            return np.nan
        val = str(val).replace('_', '').strip()
        # if val contains weird chars like !@9#%8, return nan
        if any(char in val for char in ['!', '@', '#', '$', '%', '*', '&']):
            return np.nan
        if val == '':
            return np.nan
        try:
            return float(val)
        except:
            return np.nan

    print("Cleaning 'Annual_Income'...")
    df['Annual_Income'] = df['Annual_Income'].apply(clean_numeric_str)
    
    print("Cleaning 'Outstanding_Debt'...")
    df['Outstanding_Debt'] = df['Outstanding_Debt'].apply(clean_numeric_str)
    
    # We will replace negative or invalid values with NaN
    df.loc[df['Annual_Income'] <= 0, 'Annual_Income'] = np.nan
    df.loc[df['Outstanding_Debt'] < 0, 'Outstanding_Debt'] = np.nan
    
    # Fill nulls with median for numerical columns to avoid losing rows
    df['Annual_Income'] = df['Annual_Income'].fillna(df['Annual_Income'].median())
    df['Outstanding_Debt'] = df['Outstanding_Debt'].fillna(df['Outstanding_Debt'].median())
    
    # Clean Credit Score (Good, Standard, Poor)
    print("Cleaning 'Credit_Score'...")
    # It might contain weird strings or nulls
    valid_scores = ['Good', 'Standard', 'Poor']
    df['Credit_Score'] = df['Credit_Score'].apply(lambda x: x if pd.notna(x) and str(x) in valid_scores else np.nan)
    # Fill nulls with the mode
    if not df['Credit_Score'].mode().empty:
        df['Credit_Score'] = df['Credit_Score'].fillna(df['Credit_Score'].mode()[0])
    else:
        df['Credit_Score'] = df['Credit_Score'].fillna('Standard')
    
    # Calculate Monthly Income assuming Annual / 12
    # Because sometimes 'Monthly_Inhand_Salary' is missing or weird
    df['Monthly_Income'] = df['Annual_Income'] / 12.0
    
    # Calculate DTI (Debt to Income Ratio)
    # Outstanding_Debt / Annual_Income
    df['DTI'] = df['Outstanding_Debt'] / df['Annual_Income']
    
    print(f"Cleaned shape: {df.shape}")
    
    print(f"Saving cleaned data to {output_path}...")
    df.to_csv(output_path, index=False)
    print("Done!")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(current_dir, "..", "data", "clientes.csv")
    output_csv = os.path.join(current_dir, "..", "data", "clientes_limpios.csv")
    
    clean_data(input_csv, output_csv)
