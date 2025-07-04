import random

# ==============================================================================
#      DEFINICIÓN DEL ESPACIO DE PARÁMETROS
# ==============================================================================

# Lista de todas las tandas de datos de turbulencia disponibles
tandas_disponibles = [
    'tanda1_26.03', 'tanda2_26.03', 'tanda3_26.03', 'tanda1_27.03', 'tanda2_27.03',
    'tanda3_27.03', 'tanda4_27.03', 'tanda5_27.03', 'tanda1_28.03', 'tanda2_28.03',
    'tanda1_01.04', 'tanda2_01.04', 'tanda3_01.04', 'tanda4_01.04', 'tanda1_03.04',
    'tanda2_03.04', 'tanda3_03.04', 'tanda1_14.05', 'tanda2_14.05', 'tanda3_14.05',
    'tanda4_14.05', 'tanda1_15.05', 'tanda2_15.05', 'tanda3_15.05', 'tanda4_15.05'
]

# Lista de posibles valores de Pec (Probabilidad de Cuenta Oscura)
pec_disponibles = [1e-8, 5e-8, 1e-7, 5e-7, 1e-6, 5e-6, 1e-5]

# Lista de posibles valores de QBERI (Tasa de Error Intrínseca)
qberi_disponibles = [0.005, 0.01, 0.02, 0.03, 0.04, 0.05]


# ==============================================================================
#      SELECCIÓN E IMPRESIÓN DE PARÁMETROS ALEATORIOS
# ==============================================================================

# --- CAMBIO PRINCIPAL: Elegimos 3 tandas en lugar de 1 ---
# Usamos random.sample(lista, k) para elegir k elementos únicos sin repetición.
numero_de_tandas_a_elegir = 3
tandas_elegidas = random.sample(tandas_disponibles, k=numero_de_tandas_a_elegir)

# Elegimos un solo valor para Pec y QBERI, que se usará para las 3 simulaciones
pec_elegido = random.choice(pec_disponibles)
qberi_elegido = random.choice(qberi_disponibles)

# Imprime los resultados de una manera clara y fácil de copiar
print("="*60)
print("     Parámetros Aleatorios para Comparación (3 Tandas)")
print("="*60)
print("\nParámetros del Sistema (fijos para las 3 simulaciones):")
print("-" * 60)
print(f"Pec (Cuenta Oscura):    {pec_elegido:.0e}")
print(f"QBERI (Error Intr.):    {qberi_elegido}")
print("-" * 60)
print("\nEjecuta una simulación de SatQuMA para CADA una de las siguientes tandas:")
print("-" * 60)
for i, tanda in enumerate(tandas_elegidas):
    print(f"Simulación {i+1}: Tanda de Turbulencia = '{tanda}'")
print("="*60)