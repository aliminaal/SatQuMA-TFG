import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

PEC_VAL = 1e-07
QBERI_VAL = 0.01
TANDAS_A_ANALIZAR = ['tanda1_03.04', 'tanda1_27.03', 'tanda2_14.05']
ruta_base_salidas = "/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/out"

# Unimos todos los datos en un solo DataFrame
dfs = []
for tanda in TANDAS_A_ANALIZAR:
    exponente = int(f"{PEC_VAL:e}".split('e')[-1])
    pec_str_fichero = f"1e-{abs(exponente):02d}"
    if QBERI_VAL == 0.005:
        qberi_str_fichero = f"{QBERI_VAL:.3f}"
    else:
        qberi_str_fichero = f"{QBERI_VAL:.2f}"
    nombre_fichero_base = f"results_th_m_90.00_Pec_{pec_str_fichero}_QBERI_{qberi_str_fichero}.csv"
    ruta_completa_fichero = os.path.join(ruta_base_salidas, tanda, nombre_fichero_base)

    if os.path.exists(ruta_completa_fichero):
        df = pd.read_csv(ruta_completa_fichero)
        df['Tanda'] = tanda  # Nueva columna para el nombre de la tanda
        dfs.append(df)

if len(dfs) == 0:
    print("No hay datos para graficar.")
else:
    data = pd.concat(dfs, ignore_index=True)
    # --- SCATTERPLOT ---
    plt.figure(figsize=(12, 7))
    scatter = sns.scatterplot(
        data=data,
        x='maxElev (deg)',         # Eje X
        y='SKL (b)',               # Eje Y
        hue='Tanda',               # Color por tanda
        size='SysLoss (dB)',       # Tamaño por SysLoss
        alpha=0.7,
        palette="tab10",
        sizes=(20, 200)
    )
    plt.xlabel("maxElev (deg)")
    plt.ylabel("SKL (b)")
    plt.title("SKL (b) vs maxElev (deg) | Color por tanda, Tamaño por SysLoss (dB)")
    plt.yscale('log')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2)
    plt.tight_layout()
    plt.show()
