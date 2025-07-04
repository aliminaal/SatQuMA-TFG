import os
import glob
import pandas as pd
import numpy as np

def main():
    # Carpeta donde están los CSV de Cn2
    cn2_folder = (
        "/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/"
        "SatQuMA-main/SatQuMA-main/channel/Turbulence/cn2_tandas"
    )
    pattern = os.path.join(cn2_folder, "*.csv")

    # Función para ordenar archivos por fecha y número de tanda
    def sort_key(path):
        fname = os.path.basename(path)
        date_part, tanda_part = fname.replace(".csv", "").split("_tanda")
        return pd.to_datetime(date_part, format="%Y-%m-%d"), int(tanda_part)

    files = sorted(glob.glob(pattern), key=sort_key)
    if not files:
        raise RuntimeError(f"No hay archivos CSV en {cn2_folder}")

    # Construir etiquetas: ["tanda1_DD.MM", "tanda2_DD.MM", ...]
    labels = []
    for path in files:
        base = os.path.basename(path).replace(".csv", "")
        date_part, tanda_part = base.split("_tanda")
        dt = pd.to_datetime(date_part, format="%Y-%m-%d")
        labels.append(f"tanda{int(tanda_part)}_{dt.day:02d}.{dt.month:02d}")

    n_cols = len(labels)

    # Leer y ajustar cada columna a 91 puntos
    cn2 = np.zeros((91, n_cols))
    prev = None
    for i, path in enumerate(files):
        df = pd.read_csv(path, parse_dates=["timestamp"])
        vals = df["Cn2"].values
        if vals.size > 91:
            vals = vals[:91]
        start = 91 - vals.size
        if vals.size < 91 and prev is not None:
            cn2[:start, i] = prev[-start:]
        cn2[start:, i] = vals
        prev = cn2[:, i].copy()

    # Directorio y fichero de salida
    out_dir = os.path.join(cn2_folder, "/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/channel/Turbulence")
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, "pasosCn2.py")

    # Parámetros de formato
    per_line = 5
    indent = "\t" * 5 + " "

    # Escribimos el módulo pasosCn2.py
    with open(output_path, "w") as f:
        # 1) Header de hashes
        f.write("#" * 80 + "\n\n")
        # 2) Imports y __all__
        f.write("import numpy as np\n\n")
        f.write("__all__ = ['tandas', 'elev', 'cn2', 'get_t_data']\n\n")
        # 3) Definir tandas
        f.write("tandas = np.array([\n")
        for j in range(0, len(labels), per_line):
            chunk = labels[j:j+per_line]
            line = ", ".join(f"'{lbl}'" for lbl in chunk)
            suffix = "," if j + per_line < len(labels) else ""
            f.write(f"{indent}{line}{suffix}\n")
        f.write("])\n\n")
        # 4) elev y crea cn2
        f.write("elev = np.arange(0,90+1,1)\n")
        f.write(f"cn2 = np.zeros((91,{n_cols}))\n\n")
        # 5) Cada tanda en su bloque
        for idx, lbl in enumerate(labels):
            f.write("#" * 80 + "\n\n")
            f.write(f"# {lbl}\n\n")
            col = cn2[:, idx]
            for k in range(0, 91, per_line):
                chunk = col[k:k+per_line]
                nums = ", ".join(f"{v:.8e}" for v in chunk)
                if k == 0:
                    f.write(f"cn2[:,{idx}] = np.array([{nums},\n")
                elif k + per_line < 91:
                    f.write(f"{indent}{nums},\n")
                else:
                    f.write(f"{indent}{nums}])\n\n")
        # 6) Función get_t_data basada en etiqueta de tanda
        f.write("#" * 80 + "\n\n")
        f.write("def get_t_data(tanda_label):\n")
        f.write('    """\n')
        f.write("    Devuelve la transmisión atmosférica (Cn2) en función de elevación\n")
        f.write("    para una tanda especificada.\n\n")
        f.write("    Parameters\n    ----------\n")
        f.write("    tanda_label : str\n")
        f.write("        Etiqueta de la tanda, p.e. 'tanda3_14.05'.\n\n")
        f.write("    Returns\n")
        f.write("    -------\n")
        f.write("    elev : array-like\n")
        f.write("        Ángulos de elevación (0–90°).\n")
        f.write("    cn2_vals : array-like\n")
        f.write("        Valores de Cn2 para esa tanda.\n")
        f.write('    """\n')
        f.write("    if tanda_label not in tandas:\n")
        f.write("        raise ValueError(f\"Etiqueta '{tanda_label}' no encontrada en tandas\")\n")
        f.write("    idx = np.where(tandas == tanda_label)[0][0]\n")
        f.write("    return elev, cn2[:, idx]\n")

    print(f"pasosCn2.py generado en:\n  {output_path}")

if __name__ == "__main__":
    main()
