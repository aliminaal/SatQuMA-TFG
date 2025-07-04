import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # <-- ¡LÍNEA AÑADIDA!
import os

# ==============================================================================
# SECCIÓN 1: CONFIGURACIÓN DEL ANÁLISIS
# ==============================================================================

PEC_VAL = 1e-07
QBERI_VAL = 0.01
TANDAS_A_ANALIZAR = ['tanda1_03.04', 'tanda1_27.03', 'tanda2_14.05']

ruta_proyecto_principal = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
ruta_base_salidas = os.path.join(ruta_proyecto_principal, 'out')

print("="*60)
print("Generador de Gráfico de Diagnóstico Físico (Opción 1) - v5 (Corregido)")
print("="*60)
print(f"Analizando sistema con Pec={PEC_VAL:.0e}, QBERI={QBERI_VAL}")
print(f"Comparando las tandas: {', '.join(TANDAS_A_ANALIZAR)}")
print("-" * 60)

# ==============================================================================
# SECCIÓN 2: CARGA DE DATOS Y CREACIÓN DEL GRÁFICO
# ==============================================================================

fig, ax = plt.subplots(figsize=(12, 7))
datos_encontrados = False

for tanda in TANDAS_A_ANALIZAR:
    
    # Construcción del nombre del fichero
    exponente = int(f"{PEC_VAL:e}".split('e')[-1])
    pec_str_fichero = f"1e-{abs(exponente):02d}"

    if QBERI_VAL == 0.005:
        qberi_str_fichero = f"{QBERI_VAL:.3f}"
    else:
        qberi_str_fichero = f"{QBERI_VAL:.2f}"

    nombre_fichero_base = f"results_th_m_90.00_Pec_{pec_str_fichero}_QBERI_{qberi_str_fichero}.csv"
    ruta_completa_fichero = os.path.join(ruta_base_salidas, tanda, nombre_fichero_base)
    
    print(f"Buscando datos para '{tanda}' en: {ruta_completa_fichero}")
    
    if os.path.exists(ruta_completa_fichero):
        try:
            df = pd.read_csv(ruta_completa_fichero)
            
            print(f" -> Fichero encontrado. Verificando columnas...")
            if 'Elevation (rad)' in df.columns and 'SKL (b)' in df.columns:
                
                # Gráfico de prueba temporal usando SKL
                ax.plot(
                    np.degrees(df['Elevation (rad)']),
                    df['SKL (b)'], 
                    'o-',
                    markersize=3,
                    alpha=0.7,
                    label=f"{tanda} (SKL)"
                )
                print(" -> Curva dibujada (usando SKL como ejemplo).")
                datos_encontrados = True
            else:
                print(" -> Fichero encontrado, pero faltan columnas clave ('Elevation (rad)' o 'SKL (b)'). Omitiendo.")

        except Exception as e:
            print(f" -> Error al leer el fichero para la tanda '{tanda}': {e}")
    else:
        print(f" -> ¡ADVERTENCIA! No se encontró el fichero de resultados para la tanda '{tanda}'.")

# ==============================================================================
# SECCIÓN 3: FINALIZACIÓN Y GUARDADO DEL GRÁFICO
# ==============================================================================

if datos_encontrados:
    ax.set_xlabel("Ángulo de Elevación (grados)", fontsize=12)
    ax.set_ylabel("SKL (b) [Gráfico Temporal]", fontsize=12)
    ax.set_title("Gráfico de Prueba: SKL vs. Elevación para Diferentes Tandas", fontsize=14, weight='bold')
    ax.legend(title="Tanda de Datos")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_yscale('log')
    
    nombre_grafico_salida = "grafico_prueba_skl_vs_elevacion.png"
    plt.savefig(nombre_grafico_salida, dpi=300)
    
    print("-" * 60)
    print(f"¡Gráfico generado con éxito!")
    print(f"Guardado como: '{nombre_grafico_salida}' en la carpeta actual.")
    print("RECUERDA: Este es un gráfico de prueba. Para el gráfico de diagnóstico real,")
    print("debes modificar SatQuMA para que guarde la columna 'sigma2' en los ficheros de salida.")
    print("="*60)
    
    plt.show()

else:
    print("-" * 60)
    print("No se pudo generar el gráfico. Verifica que los ficheros existen y las rutas son correctas.")
    print("="*60)