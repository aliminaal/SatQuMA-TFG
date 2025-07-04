import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MultipleLocator

# --- 1. CONFIGURACIÓN ---
data_directory = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/out/Angulos/tanda2_27.03'
output_path = '/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/plot/radianes/grafica_final_tiempo.png'

# --- Selecciona aquí la simulación que quieres graficar ---
TARGET_PEC = 1e-05
TARGET_QBERI = 0.01

# --- Mapa de estilo para replicar la apariencia visual ---
STYLE_MAP = {
    90: {'color': '#000000', 'linestyle': '-'},
    80: {'color': '#E69F00', 'linestyle': '--'}, # Naranja
    70: {'color': '#56B4E9', 'linestyle': '-.'}, # Azul cielo
    60: {'color': '#D55E00', 'linestyle': '--'}, # Naranja oscuro
    50: {'color': '#009E73', 'linestyle': '-.'}, # Verde
    45: {'color': '#0072B2', 'linestyle': '-.'}, # Azul oscuro
    40: {'color': '#0072B2', 'linestyle': ':'},  # Azul oscuro
    30: {'color': '#009E73', 'linestyle': ':'}   # Verde
}
DEFAULT_STYLE = {'color': 'gray', 'linestyle': ':'}

# Nombres de las columnas en los archivos CSV
COLUMN_NAMES = [
    'dt', 'ls', 'QBERI_val', 'Pec_val', 'maxElev', 'SKL (b)', 'QBER', 'phiX', 'nX', 'nZ', 'mX', 
    'lambdaEC', 'sX0', 'sX1', 'vZ1', 'sZ1', 'mean_photon_no', 'PxA', 'PxB', 'P1', 'P2', 'P3', 
    'mu1', 'mu2', 'mu3', 'eps_c', 'eps_s', 'Pap', 'NoPass', 'fs', 'minElev', 
    'shiftElev', 'SysLoss (dB)', 'sigma2', 'T_turb'
]

# --- 2. FUNCIÓN PARA CARGAR Y PROCESAR DATOS ---
def load_data_from_directory(directory, target_pec, target_qberi):
    all_data = []
    theta_pattern = re.compile(r'th_m_(\d+\.\d+)')
    pec_pattern = re.compile(r'Pec_([\d.eE-]+)')
    qberi_pattern = re.compile(r'QBERI_(\d+\.\d+)')

    print(f"Buscando archivos en: {directory}")
    print(f"Filtrando por: Pec ≈ {target_pec}, QBERI ≈ {target_qberi}")
    
    files_in_dir = os.listdir(directory)
        
    for filename in sorted(files_in_dir):
        if filename.startswith('results_th_m_') and filename.endswith('.csv'):
            theta_match = theta_pattern.search(filename)
            pec_match = pec_pattern.search(filename)
            qberi_match = qberi_pattern.search(filename)

            if theta_match and pec_match and qberi_match:
                try:
                    theta_val = int(float(theta_match.group(1)))
                    pec_val = float(pec_match.group(1))
                    qberi_val = float(qberi_match.group(1))

                    if np.isclose(pec_val, target_pec) and np.isclose(qberi_val, target_qberi):
                        filepath = os.path.join(directory, filename)
                        df = pd.read_csv(
                            filepath, comment='#', header=None, names=COLUMN_NAMES, on_bad_lines='skip' 
                        )
                        df['theta_max'] = theta_val
                        all_data.append(df)
                        print(f"  - ✅ Procesado: {filename}")
                except (ValueError, IndexError) as e:
                    print(f"  - ⚠️  Saltando archivo '{filename}' por formato inesperado: {e}")

    if not all_data:
        print("\nError: No se cargaron datos. Revisa los TARGET y los nombres de archivo.")
        return None

    return pd.concat(all_data, ignore_index=True)

# --- 3. EJECUCIÓN Y PREPARACIÓN DE DATOS ---
full_data = load_data_from_directory(data_directory, TARGET_PEC, TARGET_QBERI)
if full_data is None:
    exit()

# --- MODIFICACIÓN PRINCIPAL: Usar 'dt' como variable del eje X ---
COL_X_AXIS = 'dt' # <--- CAMBIO CLAVE
COL_SYSLOSS = 'SysLoss (dB)'
COL_SKL = 'SKL (b)'
COL_THETA = 'theta_max'

# Centrar el tiempo en 0. Se asume que el punto de mínima pérdida es t=0
# En tus datos, el tiempo mínimo ya es el más cercano al pico.
# Lo centraremos restando el tiempo medio para cada grupo de theta.
full_data['dt_centered'] = full_data.groupby(COL_THETA)[COL_X_AXIS].transform(lambda x: x - x.mean())
COL_X_AXIS = 'dt_centered' # Ahora usamos el tiempo centrado

# Usamos pivot_table. Ahora no debería haber duplicados con dt_centered.
heatmap_data = full_data.pivot_table(
    index=COL_THETA, columns=COL_X_AXIS, values=COL_SYSLOSS, aggfunc='mean'
)
# Interpolar para rellenar huecos en el grid, lo que suaviza el mapa de calor
heatmap_data = heatmap_data.interpolate(axis=1, limit_direction='both')

x_coords = heatmap_data.columns.values
y_coords = np.unique(heatmap_data.index.values)

# Normalizamos la tasa de clave segura (SKL)
full_data['skl_normalized'] = full_data.groupby(COL_THETA)[COL_SKL].transform(
    lambda x: x / x.max() if x.max() > 0 else 0
)

# --- 4. CREACIÓN DE LA GRÁFICA ---
sns.set_theme(style="ticks", context="talk")
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': 'Arial', 'mathtext.fontset': 'custom',
    'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold'
})

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10, 10), sharex=True, gridspec_kw={'height_ratios': [2, 2], 'hspace': 0.1}
)

# --- Panel (a): Mapa de Calor ---
cmap = plt.get_cmap('inferno_r')
im = ax1.pcolormesh(
    x_coords, y_coords, heatmap_data.loc[y_coords].values, 
    cmap=cmap, shading='gouraud', vmin=40, vmax=80
)
cbar = fig.colorbar(im, ax=ax1, orientation='horizontal', location='top', pad=0.15, aspect=40)
cbar.set_label('Transmission Loss (dB)', fontsize=16, weight='bold')
cbar.ax.tick_params(labelsize=14)

contour_levels = [45, 50, 55, 60, 70]
contour_styles = ['solid', 'dashdot', 'dashed', 'dashdot', 'solid']
CS = ax1.contour(
    x_coords, y_coords, heatmap_data.loc[y_coords].values, 
    levels=contour_levels, colors='white', linestyles=contour_styles
)
ax1.clabel(CS, inline=True, fontsize=12, fmt='%d')

ax1.set_ylabel('$\\theta_{max}$ (deg)', fontsize=16)
ax1.set_yticks(np.arange(30, 91, 30))
ax1.tick_params(axis='y', labelsize=14, direction='in')
ax1.text(-0.12, 0.9, 'a', transform=ax1.transAxes, fontsize=20, fontweight='bold', va='top')

# --- Panel (b): Curvas de SKL ---
thetas_to_plot = sorted(full_data[COL_THETA].unique(), reverse=True)
for theta in thetas_to_plot:
    style = STYLE_MAP.get(theta, DEFAULT_STYLE)
    subset = full_data[full_data[COL_THETA] == theta].sort_values(COL_X_AXIS)
    ax2.plot(
        subset[COL_X_AXIS], subset['skl_normalized'], label=f'{theta}',
        color=style['color'], linestyle=style['linestyle'], linewidth=3
    )

legend = ax2.legend(title='$\\theta_{max}$ (deg)', fontsize=14, title_fontsize=16, frameon=False)
ax2.set_xlabel(r't (s)', fontsize=16)
ax2.set_ylabel(r'Normalized SKL, $\eta_{SKL}$', fontsize=16)
ax2.tick_params(axis='both', labelsize=14, direction='in')
ax2.set_ylim(0, 1.05)
ax2.yaxis.set_major_locator(MultipleLocator(0.5))
ax2.text(-0.12, 0.9, 'b', transform=ax2.transAxes, fontsize=20, fontweight='bold', va='top')

# --- 5. AJUSTE FINAL Y GUARDADO ---
output_dir = os.path.dirname(output_path)
os.makedirs(output_dir, exist_ok=True)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Gráfica guardada exitosamente en: {output_path}")

plt.show()