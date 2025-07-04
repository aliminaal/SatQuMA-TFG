import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re
from datetime import datetime
import random

print("Iniciando la creación del gráfico con 6 recuadros aleatorios...")

# --- 1. CONFIGURACIÓN ---
base_path = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/out/'
output_dir = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/plot/Histogramas/'
os.makedirs(output_dir, exist_ok=True)

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

tanda_order_map = {
    'tanda1_26.03': "2025-03-26 12:32", 'tanda2_26.03': "2025-03-26 14:35", 'tanda3_26.03': "2025-03-26 16:08",
    'tanda1_27.03': "2025-03-27 09:38", 'tanda2_27.03': "2025-03-27 11:12", 'tanda3_27.03': "2025-03-27 12:54", 'tanda4_27.03': "2025-03-27 14:28", 'tanda5_27.03': "2025-03-27 16:02",
    'tanda1_28.03': "2025-03-28 09:16", 'tanda2_28.03': "2025-03-28 10:50",
    'tanda1_01.04': "2025-04-01 10:38", 'tanda2_01.04': "2025-04-01 12:16", 'tanda3_01.04': "2025-04-01 13:50", 'tanda4_01.04': "2025-04-01 15:26",
    'tanda1_03.04': "2025-04-03 17:00", 'tanda2_03.04': "2025-04-03 18:35", 'tanda3_03.04': "2025-04-03 20:11",
    'tanda1_14.05': "2025-05-14 09:50", 'tanda2_14.05': "2025-05-14 11:24", 'tanda3_14.05': "2025-05-14 13:00", 'tanda4_14.05': "2025-05-14 14:33",
    'tanda1_15.05': "2025-05-15 10:15", 'tanda2_15.05': "2025-05-15 11:46", 'tanda3_15.05': "2025-05-15 13:17", 'tanda4_15.05': "2025-05-15 14:51"
}

# --- 2. FUNCIÓN DE CARGA ---
def load_and_label_data(base_path, tanda_map, sin_turb_dir):
    all_dfs = []
    # Procesar tandas con turbulencia
    for tanda_dir, condicion in tanda_map.items():
        tanda_path = os.path.join(base_path, tanda_dir)
        if not os.path.isdir(tanda_path): continue
        for filename in os.listdir(tanda_path):
            if filename.endswith('.csv'):
                try:
                    df = pd.read_csv(os.path.join(tanda_path, filename))
                    df.columns = [col.strip().lstrip('#').strip() for col in df.columns]
                    pec_match = re.search(r'Pec_([\d.eE+-]+)', filename)
                    qberi_match = re.search(r'QBERI_([\d.]+)', filename)
                    if pec_match and qberi_match:
                        df['Pec'] = float(pec_match.group(1).rstrip('.'))
                        df['QBERI'] = float(qberi_match.group(1).rstrip('.'))
                        df['Condición'] = condicion
                        df['Tanda'] = tanda_dir
                        all_dfs.append(df)
                except Exception: pass
    
    # Procesar tanda SIN turbulencia
    path_sin_turb = os.path.join(base_path, sin_turb_dir)
    if os.path.isdir(path_sin_turb):
        for filename in os.listdir(path_sin_turb):
            if filename.endswith('.csv'):
                try:
                    df = pd.read_csv(os.path.join(path_sin_turb, filename))
                    df.columns = [col.strip().lstrip('#').strip() for col in df.columns]
                    pec_match = re.search(r'Pec_([\d.eE+-]+)', filename)
                    qberi_match = re.search(r'QBERI_([\d.]+)', filename)
                    if pec_match and qberi_match:
                        df['Pec'] = float(pec_match.group(1).rstrip('.'))
                        df['QBERI'] = float(qberi_match.group(1).rstrip('.'))
                        df['Tanda'] = 'Sin Turbulencia'
                        df['Condición'] = 'Sin Turbulencia'
                        all_dfs.append(df)
                except Exception: pass

    if not all_dfs: return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

# --- 3. PROCESAMIENTO ---
all_data = load_and_label_data(base_path, tanda_map, tanda_sin_turbulencia_dir)
if all_data.empty:
    print("\nERROR: No se cargaron datos.")
    exit()

zero_skl_df = all_data[all_data['SKL (b)'] == 0].copy()
count_df = zero_skl_df.groupby(['Pec', 'QBERI', 'Tanda', 'Condición']).size().reset_index(name='Conteo de Fallos')

if count_df.empty:
    print("\nNo se encontraron casos con SKL=0.")
    exit()

# --- 4. SELECCIÓN ALEATORIA Y GENERACIÓN DE GRÁFICO ---
unique_combinations = count_df[['Pec', 'QBERI']].drop_duplicates().values.tolist()
if len(unique_combinations) < 6:
    print(f"ADVERTENCIA: Solo se encontraron {len(unique_combinations)} combinaciones de Pec/QBERI. Se mostrarán todas.")
    sample_combinations = unique_combinations
    n_rows, n_cols = 1, len(unique_combinations)
else:
    sample_combinations = random.sample(unique_combinations, 6)
    n_rows, n_cols = 2, 3

fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 6, n_rows * 5), sharey=True)
axes = axes.flatten() # Facilita la iteración

print(f"Generando {len(sample_combinations)} subgráficos aleatorios...")

# Paleta de colores nueva y profesional
palette = {'Soleado': "#63b3de", 'Nublado': "#de5656", 'Sin Turbulencia': "#27EF7A"}
hue_order = ['Soleado', 'Nublado', 'Sin Turbulencia']
order_keys = ['Sin Turbulencia'] + sorted(tanda_map.keys(), key=lambda k: datetime.strptime(tanda_order_map.get(k, "1970-01-01 00:00"), "%Y-%m-%d %H:%M"))


for i, (pec, qberi) in enumerate(sample_combinations):
    ax = axes[i]
    subplot_data = count_df[(count_df['Pec'] == pec) & (count_df['QBERI'] == qberi)]
    
    sns.barplot(
        data=subplot_data,
        x='Tanda',
        y='Conteo de Fallos',
        hue='Condición',
        palette=palette,
        order=order_keys,
        hue_order=hue_order,
        ax=ax,
        dodge=False
    )
    
    ax.set_title(f'Pec = {pec:.1e}, QBERI = {qberi}', fontsize=12)
    ax.tick_params(axis='x', rotation=90)
    ax.set_xticks([])
    ax.set_xlabel('') # Quitar etiquetas X individuales
    if i % n_cols != 0: # Quitar etiquetas Y de gráficos intermedios
        ax.set_ylabel('')
        ax.set_xticklabels([])

# Ocultar los ejes de los subplots no utilizados
for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

# --- 5. AJUSTES FINALES ---
fig.suptitle("Conteo de Fallos de Comunicación (SKL=0) por Tanda y Parámetros", y=1.02, weight='bold', fontsize=18)
fig.supxlabel('Tanda de Simulación', y=0.01, fontsize=12)
fig.supylabel('Número de Fallos (SKL=0)', x=0.02, fontsize=12)

# Crear y mover la leyenda
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, title='Condición Climática', bbox_to_anchor=(1.0, 0.5), loc='center left')

plt.tight_layout(rect=[0.03, 0.03, 0.88, 0.96]) # Ajustar para dar espacio a la leyenda y títulos

# --- 6. GUARDAR ---
output_filename = os.path.join(output_dir, 'conteo_fallos_facetado_aleatorio.pdf')
plt.savefig(output_filename, format='pdf')
print(f"\n¡Éxito! Gráfico guardado en: {output_filename}")
plt.show()