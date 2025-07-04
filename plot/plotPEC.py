from pathlib import Path

# --- Rutas base (ajusta si tuvieras otra estructura) ---
ROOT   = Path("/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main")
PARSE  = ROOT / "parse_datos"
PLOT   = ROOT / "plot"

# Asegúrate de que la carpeta 'plot' exista
PLOT.mkdir(parents=True, exist_ok=True)

# --- Recorremos las carpetas dentro de parse_datos ---
for d in PARSE.iterdir():
    if not d.is_dir():
        continue                      # saltar si no es carpeta
    name = d.name

    # Filtrado deseado
    if name.startswith("tanda") and name.endswith("_parsed"):
        # Construir nombre destino sin "_parsed" y con sufijo vsSenseTurbulencia
        dest_name  = name.replace("_parsed", "") + "vsSenseTurbulencia"
        dest_path  = PLOT / dest_name

        # Crear la carpeta destino (si no existe)
        dest_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Creada o ya existe: {dest_path}")

    else:
        # Ignoramos 'SenseTurbulencia_parsed', '._parsed' y cualquier otro
        print(f"– Ignorada: {name}")

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# --- 1. CONFIGURACIÓN ---
ROOT = Path("/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main")
DATA_ROOT = ROOT / "parse_datos"
PLOTS_ROOT = ROOT / "plot"

SENSE_DATA_DIR = DATA_ROOT / "SenseTurbulencia_parsed" / "datos_procesados"

# Vectores de parámetros con los 7 valores
PECS = ["1e-08", "5e-08", "1e-07", "5e-07", "1e-06", "5e-06", "1e-05"]
QBERS = ["0.005", "0.01", "0.02", "0.03", "0.04", "0.05"]

# --- AJUSTES DE ESTILO ---
# 1. Nueva paleta de colores de alto contraste para 7 líneas
high_contrast_colors = [
    '#E6194B',  # Rojo
    '#3CB44B',  # Verde
    '#FFE119',  # Amarillo
    '#4363D8',  # Azul
    '#F58231',  # Naranja
    '#911EB4',  # Púrpura
    '#42D4F4',  # Cian (Azul flojo)
]
color_map = {pec: color for pec, color in zip(PECS, high_contrast_colors)}

# 2. Estilo de línea de referencia cambiado a discontinuo ('dashed')
linestyle_map = {
    "SenseTurbulencia": "--",  # Discontinuo
    "Tanda": "-"               # Sólido
}
# --- FIN DE AJUSTES DE ESTILO ---

# --- 2. FUNCIÓN AUXILIAR PARA CARGAR Y PROCESAR DATOS ---
def load_and_process_csv(file_path):
    try:
        df = pd.read_csv(file_path, comment=None, skipinitialspace=True)
        df = df.rename(columns={df.columns[0]: df.columns[0].lstrip('# ')})
    except Exception as e:
        print(f"  [ERROR] No se pudo leer {file_path.name}: {e}")
        return pd.DataFrame()

    x_axis_col = 'SysLoss (dB)'
    y_axis_col = 'SKL (b)'

    if x_axis_col not in df.columns or y_axis_col not in df.columns:
        return pd.DataFrame()
    
    df = df[[x_axis_col, y_axis_col]].rename(columns={
        x_axis_col: 'x_axis_val',
        y_axis_col: 'skl_bits'
    })

    df['x_axis_val'] = pd.to_numeric(df['x_axis_val'], errors='coerce')
    df['skl_bits'] = pd.to_numeric(df['skl_bits'], errors='coerce')
    df.dropna(inplace=True)

    agg_df = df.groupby('x_axis_val').agg(skl_bits=('skl_bits', 'max')).reset_index()
    return agg_df[agg_df['skl_bits'] > 0]

# --- 3. LÓGICA PRINCIPAL ---
PLOTS_ROOT.mkdir(exist_ok=True)

for q_fixed in QBERS:
    print(f"\n--- Procesando para QBERI fijo = {q_fixed} ---")
    
    sense_data_for_qber = {}
    for pec in PECS:
        file_pattern = f"*Pec_{pec}_*QBERI_{q_fixed}_*.csv"
        matching_files = list(SENSE_DATA_DIR.glob(file_pattern))
        if matching_files:
            sense_data_for_qber[pec] = load_and_process_csv(matching_files[0])
    
    tanda_folders = sorted([d for d in DATA_ROOT.glob("tanda*_parsed") if d.is_dir()])
    for tanda_dir in tanda_folders:
        tanda_name = tanda_dir.name.replace("_parsed", "")
        print(f"  Procesando Tanda: {tanda_name}")

        output_dir = PLOTS_ROOT / f"{tanda_name}vsSenseTurbulencia"
        output_dir.mkdir(exist_ok=True)
        
        tanda_data_for_qber = {}
        tanda_data_dir = tanda_dir / "datos_procesados"
        for pec in PECS:
            file_pattern = f"*Pec_{pec}_*QBERI_{q_fixed}_*.csv"
            matching_files = list(tanda_data_dir.glob(file_pattern))
            if matching_files:
                all_turb_dfs = [load_and_process_csv(f) for f in matching_files]
                combined_df = pd.concat(all_turb_dfs, ignore_index=True)
                
                if not combined_df.empty:
                    final_df = combined_df.groupby('x_axis_val').agg(skl_bits=('skl_bits', 'max')).reset_index()
                    tanda_data_for_qber[pec] = final_df
        
        fig, ax = plt.subplots(figsize=(8, 6))
        legend_handles = []

        for pec in PECS:
            color = color_map.get(pec, "grey")
            
            # Línea discontinua para SenseTurbulencia
            if pec in sense_data_for_qber and not sense_data_for_qber[pec].empty:
                sns.lineplot(
                    data=sense_data_for_qber[pec], x="x_axis_val", y="skl_bits",
                    ax=ax, color=color, linestyle=linestyle_map["SenseTurbulencia"], linewidth=2.0
                )
            
            # Línea sólida para Tanda
            if pec in tanda_data_for_qber and not tanda_data_for_qber[pec].empty:
                sns.lineplot(
                    data=tanda_data_for_qber[pec], x="x_axis_val", y="skl_bits",
                    ax=ax, color=color, linestyle=linestyle_map["Tanda"], linewidth=2.5
                )
            
            # Crear leyenda con formato LaTeX
            pec_float = float(pec)
            base, exponent = f"{pec_float:.0e}".split('e')
            exponent = int(exponent)
            label_text = fr"$p_{{ec}} = {base} \times 10^{{{exponent}}}$"
            legend_handles.append(plt.Line2D([], [], color=color, linestyle='-', label=label_text))

        # 3. Quitar el título (se ha borrado la línea ax.set_title)
        ax.set_xlabel(r"$\eta_{loss}^{sys}$ (dB)", fontsize=14)
        ax.set_ylabel("Secret Key Length (bits)", fontsize=14)
        ax.set_yscale("log")
        
        ax.set_xlim(25, 55)
        ax.set_ylim(1e3, 1e7)
        ax.grid(True, which="both", linestyle='-', linewidth=0.5)
        ax.legend(handles=legend_handles, title="", loc="upper right", fontsize=12)
        
        pdf_name = f"Comparison_QBERI_{q_fixed.replace('.', 'p')}.pdf"
        fig.tight_layout()
        fig.savefig(output_dir / pdf_name, bbox_inches="tight")
        plt.close(fig)
        
        print(f"    ✓ Figura guardada en: {output_dir / pdf_name}")

print("\n--- Proceso completado ---")