#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

def chunk_cn2_by_day(input_csv: Path, output_dir: Path, step: int = 91):
    """
    Lee el CSV maestro, agrupa por día y crea archivos de `step` muestras (0°–90°).
    """
    # 1) Mostrar dónde escribimos
    print("✴️  Carpeta de salida:", output_dir.resolve())
    output_dir.mkdir(exist_ok=True, parents=True)

    # 2) Cargar y parsear timestamps
    df = pd.read_csv(input_csv, parse_dates=["timestamp"])
    df["date"] = df["timestamp"].dt.date

    # 3) Por cada día, partir en bloques de `step`
    for date, group in df.groupby("date"):
        group = group.reset_index(drop=True)
        total = len(group)
        n_chunks = (total + step - 1) // step
        print(f"{date}: {total} muestras → {n_chunks} tandas")

        for i in range(n_chunks):
            start = i * step
            end   = start + step
            sub   = group.iloc[start:end].copy()
            sub["timestamp"] = sub["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

            fname = f"{date}_tanda{i+1}.csv"
            (output_dir / fname).write_text(
                sub[["timestamp","Cn2"]].to_csv(index=False)
            )
            print("  • creado", fname)

if __name__ == "__main__":
    # 4) Ajusta aquí según dónde esté tu CSV y donde quieras los trozos
    input_csv  = Path("/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/channel/Turbulence/cn2_data.csv")
    output_dir = Path("/Users/minaal/Documents/TFG/BIJAY SOFTWARE SIMULATOR QKD/SatQuMA-main/SatQuMA-main/channel/Turbulence/cn2_tandas")

    chunk_cn2_by_day(input_csv, output_dir, step=91)
