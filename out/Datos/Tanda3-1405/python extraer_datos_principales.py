import os
import pandas as pd

# Ruta base
base_path = "/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/out/Datos/Tanda3-1405"


# Columnas que queremos extraer
columnas_deseadas = [
    'dt (s)', 'ls (dB)', 'QBERI', 'Pec', 'maxElev (deg)', 
    'SKL (b)', 'QBER', 'fs (Hz)', 'minElev (deg)', 
    'shiftElev (deg)', 'SysLoss (dB)'
]

# Recorremos todas las subcarpetas de Tanda3-1405
for folder_name in os.listdir(base_path):
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.isdir(folder_path):
        continue

    # Buscar archivo que contenga 'results_th_m'
    for file in os.listdir(folder_path):
        if 'results_th_m' in file and file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)

            # Leer la cabecera comentada con "#"
            with open(file_path, 'r') as f:
                header_line = f.readline().replace("#", "").strip()
            columnas_archivo = [col.strip() for col in header_line.split(',')]

            # Leer los datos sin cabecera
            df = pd.read_csv(file_path, skiprows=1, header=None)
            df.columns = columnas_archivo

            # Filtrar las columnas deseadas si existen
            columnas_presentes = [col for col in columnas_deseadas if col in df.columns]
            df_filtrado = df[columnas_presentes]

            # Ruta del nuevo CSV (en la raíz Tanda3-1405)
            output_path = os.path.join(base_path, f"{folder_name}.csv")
            df_filtrado.to_csv(output_path, index=False)

            print(f"✅ Generado: {folder_name}.csv")
            break  # Solo procesar un archivo por carpeta
