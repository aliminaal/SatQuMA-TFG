import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re
from datetime import datetime

print("Iniciando la creación del gráfico de conteos de SKL=0 (versión final)...")

# --- 1. CONFIGURACIÓN ---
base_path = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/out/'
output_dir = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/plot/Histogramas/'
os.makedirs(output_dir, exist_ok=True)

# Mapeo de condiciones climáticas
tanda_map = {
    'tanda1_26.03': 'Soleado', 'tanda2_26.03': 'Nublado', 'tanda3_26.03': 'Nublado',
    'tanda1_27.03': 'Nublado', 'tanda2_27.03': 'Soleado', 'tanda3_27.03': 'Soleado', 'tanda4_27.03': 'Nublado', 'tanda5_27.03': 'Nublado',
    'tanda1_28.03': 'Soleado', 'tanda2_28.03': 'Soleado',
    'tanda1_01.04': 'Soleado', 'tanda2_01.04': 'Soleado', 'tanda3_01.04': 'Soleado', 'tanda4_01.04': 'Soleado', 
    'tanda1_03.04': 'Nublado', 'tanda2_03.04': 'Nublado', 'tanda3_03.04': 'Nublado',
    'tanda1_14.05': 'Soleado', 'tanda2_14.05': 'Soleado', 'tanda3_14.05': 'Soleado', 'tanda4_14.05': 'Soleado',
    'tanda1_15.05': 'Soleado', 'tanda2_15.05': 'Soleado', 'tanda3_15.05': 'Nublado', 'tanda4_15.05': 'Nublado'
}
tanda_sin_turbulencia_dir = 'SenseTurbulencia'

# Mapeo de orden cronológico
tanda_order_map = {
    'tanda1_26.03': "2025-03-26 12:32", 'tanda2_26.03': "2025-03-26 14:35", 'tanda3_26.03': "2025-03-26 16:08",
    'tanda1_27.03': "2025-03-27 09:38", 'tanda2_27.03': "2025-03-27 11:12", 'tanda3_27.03': "2025-03-27 12:54", 'tanda4_27.03': "2025-03-27 14:28", 'tanda5_27.03': "2025-03-27 16:02",
    'tanda1_28.03': "2025-03-28 09:16", 'tanda2_28.03': "2025-03-28 10:50",
    'tanda1_01.04': "2025-04-01 10:38", 'tanda2_01.04': "2025-04-01 12:16", 'tanda3_01.04': "2025-04-01 13:50", 'tanda4_01.04': "2025-04-01 15:26",
    'tanda1_03.04': "2025-04-03 17:00", 'tanda2_03.04': "2025-04-03 18:35", 'tanda3_03.04': "2025-04-03 20:11",
    'tanda1_14.05': "2025-05-14 09:50", 'tanda2_14.05': "2025-05-14 11:24", 'tanda3_14.05': "2025-05-14 13:00", 'tanda4_14.05': "2025-05-14 14:33",
    'tanda1_15.05': "2025-05-15 10:15", 'tanda2_15.05': "2025-05-15 11:46", 'tanda3_15.05': "2025-05-15 13:17", 'tanda4_15.05': "2025-05-15 14:51"
}


# --- 2. FUNCIÓN DE CARGA Y ETIQUETADO ---
def load_and_label_data(base_path, tanda_map, sin_turb_dir):
    all_dfs = []
    print("Cargando y etiquetando datos...")
    
    # Procesar tandas con turbulencia
    for tanda_dir, condicion in tanda_map.items():
        tanda_path = os.path.join(base_path, tanda_dir)
        if not os.path.isdir(tanda_path): continue
        for filename in os.listdir(tanda_path):
            if filename.endswith('.csv'):
                try:
                    df = pd.read_csv(os.path.join(tanda_path, filename))
                    df.columns = [col.strip().lstrip('#').strip() for col in df.columns]
                    df['Tanda'] = tanda_dir
                    df['Condición'] = condicion
                    all_dfs.append(df)
                except Exception as e:
                    print(f"    -> Error en {tanda_dir}/{filename}: {e}")

    # Procesar tanda SIN turbulencia
    path_sin_turb = os.path.join(base_path, sin_turb_dir)
    if os.path.isdir(path_sin_turb):
        print(f"  Procesando: {sin_turb_dir}")
        for filename in os.listdir(path_sin_turb):
            if filename.endswith('.csv'):
                try:
                    df = pd.read_csv(os.path.join(path_sin_turb, filename))
                    df.columns = [col.strip().lstrip('#').strip() for col in df.columns]
                    df['Tanda'] = 'Sin Turbulencia' # Etiqueta especial
                    df['Condición'] = 'Sin Turbulencia'
                    all_dfs.append(df)
                except Exception as e:
                    print(f"    -> Error en {sin_turb_dir}/{filename}: {e}")

    if not all_dfs: return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

# --- 3. PROCESAMIENTO PRINCIPAL ---
all_data = load_and_label_data(base_path, tanda_map, tanda_sin_turbulencia_dir)
if all_data.empty:
    print("\nERROR: No se cargaron datos.")
    exit()

all_data.dropna(subset=['SKL (b)', 'Pec', 'QBERI'], inplace=True)
zero_skl_df = all_data[all_data['SKL (b)'] == 0].copy()
count_df = zero_skl_df.groupby(['Pec', 'QBERI', 'Tanda', 'Condición']).size().reset_index(name='Conteo de Fallos')
print(f"\nProcesamiento completo. Total de fallos (SKL=0) a graficar: {len(zero_skl_df)}")

if count_df.empty:
    print("\nNo se encontraron casos con SKL=0.")
    exit()
    
# --- 4. GENERACIÓN DEL GRÁFICO ---
print("Generando el gráfico de barras facetado...")
hue_order = ['Soleado', 'Nublado', 'Sin Turbulencia']
palette = {'Soleado': '#FFC300', 'Nublado': '#5B2C6F', 'Sin Turbulencia': '#2ECC71'}
order_keys = ['Sin Turbulencia'] + sorted(tanda_map.keys(), key=lambda k: datetime.strptime(tanda_order_map[k], "%Y-%m-%d %H:%M"))

g = sns.catplot(
    data=count_df,
    x='Tanda',
    y='Conteo de Fallos',
    hue='Condición',
    kind='bar',
    col="QBERI",
    row="Pec",
    palette=palette,
    order=order_keys,
    hue_order=hue_order,
    height=4,
    aspect=1.5,
    legend=False,
    facet_kws={} # CORRECCIÓN: Diccionario completamente vacío
)

# --- 5. AJUSTES Y TÍTULOS ---
g.fig.suptitle("Conteo de Fallos (SKL=0) por Tanda y Parámetros", y=1.03, weight='bold', fontsize=18)
g.set_axis_labels("Tanda de Simulación", "Número de Fallos (SKL=0)")
g.set_titles(row_template="Pec = {row_name:.1e}", col_template="QBERI = {col_name}")
g.set_xticklabels(rotation=90)

plt.legend(title='Condición Climática', handles=[plt.Rectangle((0,0),1,1, color=palette[label]) for label in hue_order], labels=hue_order, bbox_to_anchor=(1.05, 0.5), loc='center left')
plt.tight_layout(rect=[0, 0, 0.9, 0.96])

# --- 6. GUARDAR ---
output_filename = os.path.join(output_dir, 'conteo_fallos_por_tanda_final.pdf')
plt.savefig(output_filename, format='pdf')
print(f"\n¡Éxito! Gráfico guardado en: {output_filename}")
plt.show()