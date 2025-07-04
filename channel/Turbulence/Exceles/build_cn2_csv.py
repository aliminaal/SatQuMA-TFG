#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

# Nombres exactos de los tres archivos donde siempre tomamos A/B desde fila 10
KEY_FILES = {
    "Excel 26_03.xlsx",
    "Excel27_03.xlsx",
    "Excel 28_03.xlsx",
}

def list_excel_files():
    excel_dir = Path(__file__).parent
    all_files = list(excel_dir.glob("*.xlsx")) + list(excel_dir.glob("*.xls"))
    print(f"Buscando en: {excel_dir.resolve()}")
    print(f"{len(all_files)} archivos encontrados:")
    for f in all_files:
        print("  -", f.name)
    return all_files

def read_AB_from_10(file_path):
    """
    Lee columnas A y B desde la fila 10, convierte y filtra.
    """
    df = pd.read_excel(
        file_path,
        usecols="A:B",
        header=None,
        skiprows=9,
        dtype=object
    )
    df.columns = ["timestamp_raw", "Cn2_raw"]

    df["timestamp"] = pd.to_datetime(df["timestamp_raw"], errors="coerce")
    df["Cn2"]       = pd.to_numeric(    df["Cn2_raw"],       errors="coerce")

    before = len(df)
    df = df.dropna(subset=["timestamp", "Cn2"])
    after = len(df)
    print(f"{file_path.name}: {after} filas válidas de {before} (A–B desde fila 10)")
    return df[["timestamp","Cn2"]]

def read_generic(file_path):
    """
    Lógica genérica anterior: detecta fila de cabecera real en A/B,
    extrae a partir de ahí A y B o A y C según convenga.
    Aquí simplificamos: detecta cabecera en A ("timestamp") y en B ("Cn2")
    y extrae todo debajo.
    """
    df0 = pd.read_excel(file_path, usecols="A:C", header=None, dtype=object)
    df0.columns = ["A","B","C"]

    # 1) encontrar fila de cabecera
    mask_hdr = (
        df0["A"].astype(str).str.lower().str.contains("timestamp") &
        df0["B"].astype(str).str.lower().str.contains("cn2")
    )
    if not mask_hdr.any():
        print(f"⚠️ {file_path.name}: no cabecera A/B → intento A/C")
        # buscar A/C
        mask_hdr = (
            df0["A"].astype(str).str.lower().str.contains("timestamp") &
            df0["C"].astype(str).str.lower().str.contains("cn2")
        )
        if not mask_hdr.any():
            print(f"⚠️ {file_path.name}: tampoco cabecera A/C → lo ignoro.")
            return pd.DataFrame(columns=["timestamp","Cn2"])
        hdr = mask_hdr.idxmax()
        ts_col, cn2_col = "A","C"
    else:
        hdr = mask_hdr.idxmax()
        ts_col, cn2_col = "A","B"

    # 2) extraer desde fila siguiente
    df_data = df0.iloc[hdr+1:].copy()[[ts_col, cn2_col]]
    df_data.columns = ["timestamp_raw","Cn2_raw"]

    # 3) convertir y filtrar
    df_data["timestamp"] = pd.to_datetime(df_data["timestamp_raw"], errors="coerce")
    df_data["Cn2"]       = pd.to_numeric(    df_data["Cn2_raw"],       errors="coerce")
    before = len(df_data)
    df_data = df_data.dropna(subset=["timestamp","Cn2"])
    after = len(df_data)
    print(f"{file_path.name}: {after} filas válidas de {before} (genérico)")
    return df_data[["timestamp","Cn2"]]

def main():
    files = list_excel_files()
    cleaned = []

    for f in files:
        print(f"\nProcesando {f.name} …")
        if f.name in KEY_FILES:
            df = read_AB_from_10(f)
        else:
            df = read_generic(f)
        if not df.empty:
            cleaned.append(df)

    if not cleaned:
        print("❌ Ningún archivo produjo datos válidos.")
        return

    # concatenar, ordenar y guardar
    all_data = pd.concat(cleaned, ignore_index=True)
    all_data = all_data.sort_values("timestamp").reset_index(drop=True)
    all_data["timestamp"] = all_data["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    output_csv = Path(__file__).parent.parent / "cn2_data.csv"
    all_data.to_csv(output_csv, index=False)
    print(f"\n✅ CSV final en: {output_csv.resolve()}")
    print(f"Total filas en CSV: {len(all_data)}")

if __name__ == "__main__":
    main()
