import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import numpy as np

print("Iniciando la creación del gráfico de violín (versión corregida)...")

# --- 1. CONFIGURACIÓN DE RUTAS Y PARÁMETROS ---

base_path = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/out/'

# IMPORTANTE: Reemplaza 'otra_tanda' con un nombre de carpeta que exista.
# El error de "Directorio no encontrado" es porque esta carpeta no existe.
tandas_con_turbulencia = [
    'tanda1_26.03',
    'tanda4_14.05',
    'tanda2_15.05',
    # 'otra_tanda' # Comentado para evitar el error. Añade aquí tu cuarta tanda real.
]

tanda_sin_turbulencia_dir = 'SenseTurbulencia'

TARGET_PEC = 1e-07
TARGET_QBERI = 0.04

output_dir = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/plot/Violinplot/'
os.makedirs(output_dir, exist_ok=True)


# --- 2. FUNCIÓN AUXILIAR PARA CARGAR Y FILTRAR DATOS (CORREGIDA) ---

def load_data_for_tanda(tanda_path, pec_val, qberi_val):
    """
    Busca en una carpeta todos los archivos CSV que coincidan con los valores
    de Pec y QBERI, los carga y los concatena en un único DataFrame.
    """
    if not os.path.isdir(tanda_path):
        print(f"  -> Directorio no encontrado: {tanda_path}")
        return None
        
    matching_files_dfs = []
    print(f"Buscando en: {tanda_path}")
    
    for filename in os.listdir(tanda_path):
        if filename.endswith('.csv'):
            try:
                parts = filename.replace('.csv', '').split('_')
                pec_index = parts.index('Pec')
                qberi_index = parts.index('QBERI')
                
                file_pec = float(parts[pec_index + 1])
                file_qberi = float(parts[qberi_index + 1])
                
                if np.isclose(file_pec, pec_val) and np.isclose(file_qberi, qberi_val):
                    full_path = os.path.join(tanda_path, filename)
                    
                    # --- INICIO DE LA CORRECCIÓN ---
                    # 1. Quitar comment='#' para que lea la cabecera.
                    df = pd.read_csv(full_path) 
                    
                    # 2. Limpiar los nombres de las columnas de forma robusta.
                    # Esto quita espacios y el '#' del inicio de la primera columna.
                    clean_columns = []
                    for col in df.columns:
                        clean_col = col.strip() # Quita espacios al principio y al final
                        if clean_col.startswith('#'):
                            clean_col = clean_col.lstrip('#').strip() # Quita el # y los espacios que queden
                        clean_columns.append(clean_col)
                    
                    df.columns = clean_columns
                    # --- FIN DE LA CORRECCIÓN ---
                    
                    matching_files_dfs.append(df)
                    print(f"    -> Archivo coincidente cargado: {filename}")
            
            except (ValueError, IndexError):
                continue
    
    if not matching_files_dfs:
        return None
    
    return pd.concat(matching_files_dfs, ignore_index=True)


# --- 3. PROCESAMIENTO PRINCIPAL DE DATOS (Sin cambios) ---

all_data_frames = []
path_sin_turb_dir = os.path.join(base_path, tanda_sin_turbulencia_dir)
df_sin_turb_base = load_data_for_tanda(path_sin_turb_dir, TARGET_PEC, TARGET_QBERI)

if df_sin_turb_base is None:
    print(f"\nERROR: No se encontraron archivos SIN turbulencia que coincidan con Pec={TARGET_PEC} y QBERI={TARGET_QBERI}.")
    exit()

print(f"\n-> Datos base SIN turbulencia cargados ({len(df_sin_turb_base)} filas en total).")

for tanda_name in tandas_con_turbulencia:
    print(f"\nProcesando tanda CON turbulencia: {tanda_name}...")
    current_tanda_path = os.path.join(base_path, tanda_name)
    
    df_con_turb = load_data_for_tanda(current_tanda_path, TARGET_PEC, TARGET_QBERI)
    
    if df_con_turb is not None and not df_con_turb.empty:
        clean_tanda_name = tanda_name.split('_', 1)[-1].replace('_', '.')
        df_con_turb['Tanda'] = clean_tanda_name
        df_con_turb['Condición'] = 'Con Turbulencia'
        all_data_frames.append(df_con_turb)
        
        df_sin_turb_temp = df_sin_turb_base.copy()
        df_sin_turb_temp['Tanda'] = clean_tanda_name
        df_sin_turb_temp['Condición'] = 'Sin Turbulencia'
        all_data_frames.append(df_sin_turb_temp)
        
        print(f"  -> Tanda '{tanda_name}' procesada con {len(df_con_turb)} filas.")
    else:
        print(f"  -> AVISO: No se encontraron archivos coincidentes para la tanda '{tanda_name}'. Se saltará esta tanda.")

if not all_data_frames:
    print("\nERROR: No se cargó ningún dato de las tandas con turbulencia. Revisa las rutas y los parámetros. Saliendo.")
    exit()

combined_df = pd.concat(all_data_frames, ignore_index=True)


# --- 4. LIMPIEZA FINAL Y TRANSFORMACIÓN DE DATOS (Sin cambios) ---

final_df = combined_df[['SKL (b)', 'Tanda', 'Condición']].copy()
final_df.dropna(subset=['SKL (b)'], inplace=True)
final_df['SKL (Mb)'] = final_df['SKL (b)'] / 1e6

print("\nResumen de los datos finales para el gráfico:")
print(final_df.groupby(['Tanda', 'Condición']).size().unstack(fill_value=0))


# --- 5. GENERACIÓN DEL GRÁFICO (CON LA LEYENDA CORREGIDA) ---

sns.set_theme(style="darkgrid")
print("\nGenerando el gráfico de violín...")

g = sns.catplot(
    data=final_df, 
    kind="violin", 
    x="Tanda", 
    y="SKL (Mb)", 
    hue="Condición", 
    split=True,
    palette="rocket",
    inner="quartile",
    height=6,
    aspect=1.5,
    order=sorted(final_df['Tanda'].unique())
)

g.set_axis_labels("Tanda de Simulación", "Tasa de Clave Secreta (SKL en Mb)")
g.legend.set_title("Condición Atmosférica")
g.fig.suptitle(f"Comparación de SKL (Pec={TARGET_PEC}, QBERI={TARGET_QBERI})", y=1.03)

# --- INICIO DE LA CORRECCIÓN ---
# Movemos la leyenda a la esquina superior derecha, DENTRO del gráfico.
sns.move_legend(g, "center right")
# --- FIN DE LA CORRECCIÓN ---


# --- 6. GUARDAR EL GRÁFICO (Sin cambios) ---

output_filename = os.path.join(output_dir, f'comparacion_SKL_Pec_{TARGET_PEC}_QBERI_{TARGET_QBERI}.pdf')
plt.savefig(output_filename, format='pdf', bbox_inches='tight')

print(f"\n¡Éxito! Gráfico guardado en: {output_filename}")