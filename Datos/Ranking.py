#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Análisis y Clasificación de Perfiles de Turbulencia.

Este script realiza un análisis exhaustivo de perfiles de turbulencia (Cn²)
basado en la siguiente metodología:
1.  **Cálculo de un conjunto diverso de métricas** físicas, estadísticas y
    estructurales para cada perfil.
2.  **Ranking de perfiles** para cada métrica individual, de peor a mejor.
3.  **Puntuación agregada** para identificar los escenarios que son
    consistentemente más severos ("peor caso") o más benignos ("mejor caso")
    a través de todas las métricas.

Genera tres productos finales:
- Una tabla completa de métricas y el ranking final impresos en la terminal.
- Una recomendación explícita de los escenarios de "peor" y "mejor caso".
- Un reporte detallado en formato PDF con los rankings individuales para
  cada métrica, junto con su descripción.
"""
import os
import sys
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

# --- Dependencias Externas (con manejo de errores) ---
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, PageBreak)
except ImportError:
    print("ERROR: La librería 'reportlab' no está instalada.")
    print("Por favor, instálala ejecutando: pip install reportlab")
    sys.exit(1)

# --- CONFIGURACIÓN GLOBAL ---
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
NOMBRE_ARCHIVO_PDF = 'Analisis_Turbulencia_Reporte.pdf'
RUTA_SALIDA_PDF = os.path.join(RUTA_BASE, NOMBRE_ARCHIVO_PDF)

WAVELENGTH_NM = 810
K_WAVENUMBER = 2 * np.pi / (WAVELENGTH_NM * 1e-9)
NUM_EXTREMOS = 5

# --- DICCIONARIO DE DESCRIPCIONES DE MÉTRICAS ---
DESCRIPCIONES_METRICAS: Dict[str, Dict[str, str]] = {
    'Rytov_σ²': {
        'titulo': 'Varianza de Rytov (Rytov_σ²)',
        'descripcion': 'Métrica física fundamental que cuantifica la intensidad del centelleo. Un valor más alto indica una mayor degradación de la señal debido a la turbulencia. Es el indicador más importante del impacto en el canal.'
    },
    'Promedio_Cn2': {
        'titulo': 'Promedio del Perfil de Turbulencia (Promedio_Cn2)',
        'descripcion': 'Es el valor medio de la intensidad de la turbulencia (Cn²) a lo largo de toda la trayectoria. Un promedio alto sugiere condiciones de turbulencia consistentemente fuertes.'
    },
    'Picos_P95_Cn2': {
        'titulo': 'Picos de Turbulencia (Percentil 95 de Cn²)',
        'descripcion': 'Representa los valores de turbulencia más altos, ignorando el 5% más extremo para evitar valores atípicos. Identifica la magnitud de las capas de turbulencia más intensas.'
    },
    'Variabilidad_Std': {
        'titulo': 'Variabilidad del Perfil (Desviación Estándar)',
        'descripcion': 'Mide la dispersión de los valores de Cn² a lo largo del perfil. Un valor alto indica que la intensidad de la turbulencia no es uniforme y fluctúa mucho con la altitud.'
    },
    'Volatilidad_Total': {
        'titulo': 'Volatilidad o "Rugosidad" del Perfil',
        'descripcion': 'Suma de los cambios absolutos entre puntos consecutivos. Un valor alto significa que el perfil es muy "dentado", con muchos cambios bruscos y rápidos de intensidad.'
    },
    'Max_Salto_Cn2': {
        'titulo': 'Máximo Cambio Abrupto (Max_Salto_Cn2)',
        'descripcion': 'Identifica el salto individual más grande entre dos altitudes consecutivas. Aísla el evento de cambio más violento en todo el perfil.'
    },
    'Rango_Amplitud_Cn2': {
        'titulo': 'Rango Dinámico del Perfil (Pico a Valle)',
        'descripcion': 'Diferencia entre el valor máximo y mínimo de Cn². Un rango alto indica que la tanda experimenta tanto capas muy fuertes como zonas de calma casi total.'
    },
    'Asimetria_Skew': {
        'titulo': 'Asimetría del Perfil (Skewness)',
        'descripcion': 'Mide la asimetría de la distribución de turbulencia. Un valor positivo alto indica que la mayoría de los valores son bajos, pero hay una "cola" de picos muy altos.'
    },
    'Curtosis_Kurt': {
        'titulo': 'Curtosis del Perfil (Kurtosis)',
        'descripcion': 'Mide qué tan "puntiaguda" es la distribución de turbulencia. Un valor alto indica que los picos extremos son más frecuentes o intensos de lo normal.'
    }
}

# --- FUNCIONES DE ANÁLISIS ---

def calcular_todas_metricas(
    cn2_data: np.ndarray,
    nombres_tandas: List[str],
    alturas_data_km: np.ndarray
) -> pd.DataFrame:
    """
    Calcula un conjunto completo de métricas para cada perfil de turbulencia.
    ...
    """
    alturas_m = alturas_data_km * 1000
    lista_metricas = []

    for i, nombre in enumerate(nombres_tandas):
        perfil = cn2_data[:, i]
        integral_cn2 = np.trapz(perfil, alturas_m)
        sigma_r_zenith = 1.23 * (K_WAVENUMBER**(7/6)) * integral_cn2
        diferencias = np.diff(perfil)
        
        metricas_tanda = {
            'Tanda': nombre,
            'Rytov_σ²': sigma_r_zenith,
            'Promedio_Cn2': np.mean(perfil),
            'Picos_P95_Cn2': np.percentile(perfil, 95),
            'Variabilidad_Std': np.std(perfil),
            'Asimetria_Skew': skew(perfil),
            'Curtosis_Kurt': kurtosis(perfil, fisher=False),
            'Volatilidad_Total': np.sum(np.abs(diferencias)),
            'Max_Salto_Cn2': np.max(np.abs(diferencias)) if len(diferencias) > 0 else 0,
            'Rango_Amplitud_Cn2': np.ptp(perfil),
        }
        lista_metricas.append(metricas_tanda)
        
    df = pd.DataFrame(lista_metricas).set_index('Tanda')
    return df[list(DESCRIPCIONES_METRICAS.keys())]


def generar_matriz_rankings(df_metricas: pd.DataFrame) -> pd.DataFrame:
    """
    Crea un DataFrame donde cada columna contiene los nombres de las tandas
    ordenadas (rankeadas) de peor a mejor según esa métrica.
    ...
    """
    df_rankings = pd.DataFrame()
    for col in df_metricas.columns:
        tandas_ordenadas = df_metricas.sort_values(by=col, ascending=False).index.values
        df_rankings[f'Ranking_{col}'] = tandas_ordenadas
    return df_rankings


def analizar_puntuacion_extremos(
    df_rankings: pd.DataFrame,
    num_top: int,
    nombres_tandas: List[str]
) -> pd.DataFrame:
    """
    Calcula una puntuación agregada para identificar los escenarios más extremos.

    **Metodología:**
    Mediante esta función de puntuación se identifican las tandas que aparecen
    con mayor frecuencia en los extremos (mejores o peores) de todas las métricas.
    A cada tanda se le asigna:
    - +1 punto por cada vez que aparece en el Top N (peor) de un ranking.
    - -1 punto por cada vez que aparece en el Bottom N (mejor) de un ranking.

    Ello conduce a dos casos de referencia:
    - **Escenario "peor caso":** La tanda con la puntuación más alta. Es el perfil
      más severo, idóneo para pruebas de estrés.
    - **Escenario "mejor caso":** La tanda con la puntuación más baja. Es el perfil
      más benigno, utilizado como punto de referencia bajo condiciones casi ideales.

    Args:
        df_rankings: DataFrame de rankings generado por `generar_matriz_rankings`.
        num_top: Número de posiciones a considerar como "extremo" (ej. 5).
        nombres_tandas: Lista completa de nombres de tandas.

    Returns:
        Un DataFrame con las tandas y su puntuación final, ordenado de mayor
        a menor puntuación.
    """
    puntuacion = pd.Series(0, index=nombres_tandas, dtype=int)
    
    for col in df_rankings.columns:
        peores_tandas = df_rankings[col].head(num_top).values
        puntuacion.loc[peores_tandas] += 1
        
        mejores_tandas = df_rankings[col].tail(num_top).values
        puntuacion.loc[mejores_tandas] -= 1
        
    df_puntuacion = puntuacion.reset_index()
    df_puntuacion.columns = ['Tanda', 'Puntuacion_Extremo']
    return df_puntuacion.sort_values(by='Puntuacion_Extremo', ascending=False)


def generar_reporte_pdf(
    df_metricas: pd.DataFrame,
    descripciones: Dict[str, Any],
    output_path: str
) -> None:
    """
    Genera un reporte PDF detallado con rankings por cada métrica.
    ...
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    styles = getSampleStyleSheet()
    story = []

    titulo_principal = Paragraph("Reporte de Análisis de Perfiles de Turbulencia", styles['h1'])
    story.append(titulo_principal)
    story.append(Spacer(1, 0.25 * inch))
    intro_texto = Paragraph(
        "Este documento presenta el ranking de las tandas de simulación según "
        "diferentes métricas de turbulencia atmosférica. Cada sección detalla una "
        "métrica, su significado y la clasificación de las tandas de la más a la "
        "menos severa.", styles['Normal']
    )
    story.append(intro_texto)
    story.append(PageBreak())

    for col_name, info in descripciones.items():
        titulo_metrica = Paragraph(f"Ranking por: {info['titulo']}", styles['h2'])
        story.append(titulo_metrica)
        story.append(Spacer(1, 0.1 * inch))
        descripcion_metrica = Paragraph(info['descripcion'], styles['Normal'])
        story.append(descripcion_metrica)
        story.append(Spacer(1, 0.2 * inch))

        df_sorted = df_metricas[[col_name]].sort_values(by=col_name, ascending=False).copy()
        df_sorted.reset_index(inplace=True)
        df_sorted[col_name] = df_sorted[col_name].apply(lambda x: f"{x:.4e}")

        data_for_table = [["Posición", "Tanda", f"Valor ({col_name})"]] + \
                         [[i+1] + row for i, row in enumerate(df_sorted.values.tolist())]
        
        table = Table(data_for_table, colWidths=[1.0 * inch, 3.0 * inch, 3.0 * inch])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkslategray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)
        story.append(table)
        story.append(PageBreak())

    try:
        doc.build(story)
        print(f"\n[OK] Reporte PDF generado exitosamente en: {output_path}")
    except Exception as e:
        print(f"\n[ERROR] No se pudo crear el archivo PDF. Causa: {e}")

# --- BLOQUE PRINCIPAL DE EJECUCIÓN ---

def main():
    """Función principal que orquesta el análisis y la generación de reportes."""
    print("--- ANÁLISIS COMPLETO DE PERFILES DE TURBULENCIA ---")

    try:
        from channel.Turbulence.pasosCn2 import tandas, cn2 as cn2_table, elev as alturas_km
        print("Datos cargados exitosamente desde el módulo 'channel.Turbulence.pasosCn2'")
    except ImportError as e:
        print("ERROR CRÍTICO: No se pudo importar el módulo 'pasosCn2'.")
        print("Asegúrate de ejecutar este script desde la carpeta raíz del proyecto.")
        print(f"Error original: {e}")
        sys.exit(1)

    df_resultados = calcular_todas_metricas(cn2_table, tandas, alturas_km)
    
    print("\n[1] TABLA COMPLETA DE MÉTRICAS (ordenada por Rytov σ²):")
    pd.set_option('display.float_format', '{:.4e}'.format)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 160)
    print(df_resultados.sort_values(by='Rytov_σ²', ascending=False).to_string())
    print("-" * 160)
    
    rankings_df = generar_matriz_rankings(df_resultados)
    
    print(f"\n[2] ANÁLISIS DE PUNTUACIÓN (Top/Bottom {NUM_EXTREMOS}):")
    print("     Puntuación: +1 por cada aparición en el Top 5 (peor), -1 por cada aparición en el Bottom 5 (mejor)")
    puntuacion_final = analizar_puntuacion_extremos(rankings_df, NUM_EXTREMOS, tandas)
    print(puntuacion_final.to_string(index=False))
    print("-" * 160)

    print("\n[3] RECOMENDACIÓN FINAL DE ESCENARIOS PARA SIMULACIÓN:")
    print("---------------------------------------------------------")
    peor_general = puntuacion_final.iloc[0]['Tanda']
    mejor_general = puntuacion_final.iloc[-1]['Tanda']
    peor_ryto = rankings_df['Ranking_Rytov_σ²'].iloc[0]

    print(f"  - **PEOR ESCENARIO CONSISTENTE:** '{peor_general}' (ideal para stress test).")
    print(f"  - **MEJOR ESCENARIO CONSISTENTE:** '{mejor_general}' (ideal para benchmark).")
    if peor_ryto != peor_general:
        print(f"  - **PEOR ESCENARIO FÍSICO (Rytov):** '{peor_ryto}' (máximo impacto físico en centelleo).")

    print("\n" + "="*80)
    print("[4] GENERANDO REPORTE PDF DETALLADO...")
    generar_reporte_pdf(df_resultados, DESCRIPCIONES_METRICAS, RUTA_SALIDA_PDF)
    print("="*80)


if __name__ == "__main__":
    main()