import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# --- 1. CONFIGURACIÓN ---
ROOT = Path("/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main")
DATA_ROOT = ROOT / "parse_datos"
PLOTS_ROOT = ROOT / "plot"

SENSE_DATA_DIR = DATA_ROOT / "SenseTurbulencia_parsed" / "datos_procesados"

# Vectores de parámetros (la lógica se invierte)
PECS_FIJOS = ["1e-08", "5e-08", "1e-07", "5e-07", "1e-06", "5e-06", "1e-05"]
QBERS_A_GRAFICAR = ["0.005", "0.01", "0.02", "0.03", "0.04", "0.05"]

# --- AJUSTES DE ESTILO ---
# 1. Paleta de colores de alto contraste para 6 líneas (QBERI)
qber_color_map = {
    "0.005": '#E6194B',  # Rojo
    "0.01":  '#3CB44B',  # Verde
    "0.02":  '#4363D8',  # Azul
    "0.03":  '#F58231',  # Naranja
    "0.04":  '#911EB4',  # Púrpura
    "0.05":  '#42D4F4',  # Cian (Azul flojo)
}

# 2. Estilo de línea
linestyle_map = {
    "SenseTurbulencia": "--",  # Discontinuo
    "Tanda": "-"               # Sólido
}
# --- FIN DE AJUSTES DE ESTILO ---

# --- 2. FUNCIÓN AUXILIAR PARA CARGAR Y PROCESAR DATOS (sin cambios) ---
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

# --- 3. LÓGICA PRINCIPAL PARA QBERI ---
PLOTS_ROOT.mkdir(exist_ok=True)

# Bucle principal: iterar sobre cada valor fijo de Pec
for pec_fixed in PECS_FIJOS:
    print(f"\n--- Procesando para Pec fijo = {pec_fixed} ---")
    
    # 1. Cargar datos de SenseTurbulencia para este Pec
    sense_data_for_pec = {}
    print("  Cargando datos de SenseTurbulencia (líneas discontinuas)...")
    for qber in QBERS_A_GRAFICAR:
        file_pattern = f"*Pec_{pec_fixed}_*QBERI_{qber}_*.csv"
        matching_files = list(SENSE_DATA_DIR.glob(file_pattern))
        if matching_files:
            sense_data_for_pec[qber] = load_and_process_csv(matching_files[0])
    
    # 2. Iterar sobre cada carpeta de 'tanda'
    tanda_folders = sorted([d for d in DATA_ROOT.glob("tanda*_parsed") if d.is_dir()])
    for tanda_dir in tanda_folders:
        tanda_name = tanda_dir.name.replace("_parsed", "")
        print(f"  Procesando Tanda: {tanda_name}")

        output_dir = PLOTS_ROOT / f"{tanda_name}vsSenseTurbulencia"
        output_dir.mkdir(exist_ok=True)
        
        tanda_data_for_pec = {}
        tanda_data_dir = tanda_dir / "datos_procesados"
        print(f"    Cargando datos de {tanda_name} (líneas sólidas)...")
        for qber in QBERS_A_GRAFICAR:
            file_pattern = f"*Pec_{pec_fixed}_*QBERI_{qber}_*.csv"
            matching_files = list(tanda_data_dir.glob(file_pattern))
            if matching_files:
                all_turb_dfs = [load_and_process_csv(f) for f in matching_files]
                combined_df = pd.concat(all_turb_dfs, ignore_index=True)
                
                if not combined_df.empty:
                    final_df = combined_df.groupby('x_axis_val').agg(skl_bits=('skl_bits', 'max')).reset_index()
                    tanda_data_for_pec[qber] = final_df
        
        # --- Inicio del Trazado de la Figura ---
        fig, ax = plt.subplots(figsize=(8, 6))
        legend_handles = []

        for qber in QBERS_A_GRAFICAR:
            color = qber_color_map.get(qber, "grey")
            
            # Línea discontinua para SenseTurbulencia
            if qber in sense_data_for_pec and not sense_data_for_pec[qber].empty:
                sns.lineplot(
                    data=sense_data_for_pec[qber], x="x_axis_val", y="skl_bits",
                    ax=ax, color=color, linestyle=linestyle_map["SenseTurbulencia"], linewidth=2.0
                )
            
            # Línea sólida para Tanda
            if qber in tanda_data_for_pec and not tanda_data_for_pec[qber].empty:
                sns.lineplot(
                    data=tanda_data_for_pec[qber], x="x_axis_val", y="skl_bits",
                    ax=ax, color=color, linestyle=linestyle_map["Tanda"], linewidth=2.5
                )
            
            # Crear leyenda con formato de porcentaje
            label_text = f"QBERI = {float(qber)*100:.1f}%"
            legend_handles.append(plt.Line2D([], [], color=color, linestyle='-', label=label_text))

        # --- Personalización final ---
        ax.set_xlabel(r"$\eta_{loss}^{sys}$ (dB)", fontsize=14)
        ax.set_ylabel("Secret Key Length (bits)", fontsize=14)
        ax.set_yscale("log")
        
        ax.set_xlim(25, 50)
        ax.set_ylim(1e4, 1e7)
        ax.grid(True, which="both", linestyle='-', linewidth=0.5)
        ax.legend(handles=legend_handles, title="", loc="upper right", fontsize=12)
        
        # Guardar la figura con un nombre que indique el Pec fijo
        pdf_name = f"Comparison_Pec_{pec_fixed.replace('.', 'p')}.pdf"
        fig.tight_layout()
        fig.savefig(output_dir / pdf_name, bbox_inches="tight")
        plt.close(fig)
        
        print(f"    ✓ Figura guardada en: {output_dir / pdf_name}")

print("\n--- Proceso completado ---")