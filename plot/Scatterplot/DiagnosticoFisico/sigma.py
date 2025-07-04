import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

print("Iniciando la creación del Gráfico 3 (versión MEJORADA)...")

# --- 1. CONFIGURACIÓN ---
base_path = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/out/'
output_dir = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/plot/Scatterplot/'
os.makedirs(output_dir, exist_ok=True)

tandas_a_procesar = [
    'tanda1_27.03', 'tanda1_03.04', 'tanda1_15.05', 'Grafico2'
]

SYSTEM_LOSS_COLUMN = 'SysLoss (dB)'
SKL_COLUMN = 'SKL (b)'
TRANSMISSIVITY_COLUMN = 'T_turb'

# --- 2. CARGA DE DATOS (os.walk) ---
def load_data_from_tandas(base_path, tanda_list):
    all_dfs = []
    print("Buscando archivos CSV...")
    for tanda_name in tanda_list:
        tanda_path = os.path.join(base_path, tanda_name)
        if not os.path.isdir(tanda_path): continue
        for root, _, files in os.walk(tanda_path):
            for filename in files:
                if filename.endswith('.csv'):
                    full_path = os.path.join(root, filename)
                    try:
                        df = pd.read_csv(full_path)
                        df.columns = [col.strip().lstrip('#').strip() for col in df.columns]
                        all_dfs.append(df)
                    except Exception as e:
                        print(f"    -> ADVERTENCIA al leer {filename}: {e}")
    if not all_dfs: return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

# --- 3. PROCESAMIENTO DE DATOS ---
combined_df = load_data_from_tandas(base_path, tandas_a_procesar)
if combined_df.empty:
    print("\nERROR: No se cargaron datos.")
    exit()

columns_needed = [SYSTEM_LOSS_COLUMN, SKL_COLUMN, TRANSMISSIVITY_COLUMN]
if not all(col in combined_df.columns for col in columns_needed):
    print("\nERROR: Faltan columnas. Requeridas:", columns_needed)
    exit()

plot_df = combined_df[columns_needed].dropna().copy()
plot_df = plot_df[plot_df[SKL_COLUMN] > 0].copy()

# --- ¡NUEVO! CREACIÓN DE CATEGORÍAS PARA T_turb ---
def categorize_transmissivity(t_turb):
    if t_turb > 0.8:
        return 'Buena (> 0.8)'
    elif t_turb > 0.1:
        return 'Media (0.1 - 0.8)'
    else:
        return 'Deep Fade (< 0.1)'

plot_df['Condicion_Turbulencia'] = plot_df[TRANSMISSIVITY_COLUMN].apply(categorize_transmissivity)
order = ['Buena (> 0.8)', 'Media (0.1 - 0.8)', 'Deep Fade (< 0.1)']
palette = {'Buena (> 0.8)': '#2ECC71', 'Media (0.1 - 0.8)': '#F39C12', 'Deep Fade (< 0.1)': '#E74C3C'}

plot_df['SKL (Mb)'] = plot_df[SKL_COLUMN] / 1e6
print(f"\nTotal de filas con SKL > 0 para graficar: {len(plot_df)}")

# --- 4. GENERACIÓN DEL GRÁFICO MEJORADO ---
print("Generando el gráfico de dispersión categórico...")
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 7))

scatter_plot = sns.scatterplot(
    data=plot_df,
    x=SYSTEM_LOSS_COLUMN,
    y='SKL (Mb)',
    hue='Condicion_Turbulencia', # Usamos la nueva columna categórica
    hue_order=order,             # Ordenamos la leyenda
    palette=palette,             # Asignamos colores (Verde, Naranja, Rojo)
    s=30,
    alpha=0.8,
    edgecolor="k",
    linewidth=0.5
)

# --- 5. AJUSTES FINALES ---
plt.title("Impacto de las Fluctuaciones por Turbulencia en la SKL", fontsize=16, pad=20, weight='bold')
plt.xlabel("Pérdida Total del Sistema (SysLoss en dB)", fontsize=12)
plt.ylabel("Tasa de Clave Secreta (SKL en Megabits)", fontsize=12)
plt.yscale('log')
plt.legend(title='Condición de Transmisividad')
plt.tight_layout()

# --- 6. GUARDAR ---
output_filename = os.path.join(output_dir, 'Impacto_Final_SKL_Categorico.pdf')
plt.savefig(output_filename, format='pdf', bbox_inches='tight')
print(f"\n¡Éxito! Gráfico mejorado guardado en: {output_filename}")
plt.show()