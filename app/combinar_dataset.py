import pandas as pd
import re
import random


df_personas = pd.read_csv('data/person_100000.csv', sep=';')
df_imagenes = pd.read_csv('data/train_labels.csv', sep=';')

def parse_age_range(age_str):
    match = re.match(r'(\d+)-(\d+)', str(age_str))
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

df_imagenes['age_min'], df_imagenes['age_max'] = zip(*df_imagenes['age'].apply(parse_age_range))

df_personas['file'] = None

imagenes_disponibles = df_imagenes.copy()

for idx, persona in df_personas.iterrows():
    edad_persona = persona['age']
    genero_persona = persona['gender']
    
    candidatas = imagenes_disponibles[
        (imagenes_disponibles['gender'] == genero_persona) &
        (imagenes_disponibles['age_min'] <= edad_persona) &
        (imagenes_disponibles['age_max'] >= edad_persona)
    ]
    
    if not candidatas.empty:
        imagen_elegida = candidatas.sample(n=1).iloc[0]
        df_personas.at[idx, 'file'] = imagen_elegida['file']
        
        imagenes_disponibles = imagenes_disponibles[
            imagenes_disponibles['file'] != imagen_elegida['file']
        ]

df_personas.to_csv('data/Datos_personales.csv', index=False, sep=';')

print("Dataset final:")
print(df_personas[['person_id', 'firstname', 'lastname', 'age', 'gender', 'file']].head(10))
print(f"\nTotal asignaciones exitosas: {df_personas['file'].notna().sum()}")