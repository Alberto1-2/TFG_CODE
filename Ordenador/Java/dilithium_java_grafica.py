import pandas as pd
import matplotlib.pyplot as plt

# Nombres de los archivos CSV de las diferentes versiones de Dilithium
files = ["Dilithium2_Performance_Iteration.csv", 
         "Dilithium3_Performance_Iteration.csv", 
         "Dilithium5_Performance_Iteration.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de Dilithium
data = {"Dilithium-2 pequeño": [], "Dilithium-2 grande": [],
        "Dilithium-3 pequeño": [], "Dilithium-3 grande": [],
        "Dilithium-5 pequeño": [], "Dilithium-5 grande": []}

# Leer y procesar cada archivo CSV
for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Imprimir las primeras filas para verificar el contenido
    print(f"Contenido de {file}:")
    print(df.head())  # Imprime las primeras filas del archivo
    
    # Asegurarse de que las columnas de tiempo sean numéricas (convertir a float)
    df["Tiempo Total Pequeño (ms)"] = pd.to_numeric(df["Tiempo Total Pequeño (ms)"], errors='coerce')
    df["Tiempo Total Grande (ms)"] = pd.to_numeric(df["Tiempo Total Grande (ms)"], errors='coerce')
    
    # Verificar si las conversiones a numérico han dejado valores NaN
    print(f"¿Hay valores NaN en {file}?:")
    print(df.isna().sum())  # Imprime el número de valores NaN por columna
    
    # Determinar la versión que corresponde al archivo
    if "Dilithium_Performance" in file:
        version_key = "Dilithium-2"
    elif "Dilithium3" in file:
        version_key = "Dilithium-3"
    elif "Dilithium5" in file:
        version_key = "Dilithium-5"
    elif "Dilithium2" in file:
        version_key = "Dilithium-2" 
    else:
        version_key = None
    
    # Verificar que la clave de versión sea correcta
    if version_key:
        print(f"Procesando {version_key}")
    
    # Procesar cada fila del archivo
    for _, row in df.iterrows():
        # Agregar los tiempos en el diccionario, dependiendo del tamaño de la firma
        data[f"{version_key} pequeño"].append(row["Tiempo Total Pequeño (ms)"])
        data[f"{version_key} grande"].append(row["Tiempo Total Grande (ms)"])

# Imprimir los datos agregados en el diccionario para verificar
print("\nContenido del diccionario de datos:")
for key, value in data.items():
    print(f"{key}: {len(value)} valores")

# Crear el diagrama de cajas
plt.figure(figsize=(12, 6))
plt.boxplot([data["Dilithium-2 pequeño"], data["Dilithium-2 grande"],
             data["Dilithium-3 pequeño"], data["Dilithium-3 grande"],
             data["Dilithium-5 pequeño"], data["Dilithium-5 grande"]],
            tick_labels=["Dilithium-2 pequeño", "Dilithium-2 grande", 
                         "Dilithium-3 pequeño", "Dilithium-3 grande", 
                         "Dilithium-5 pequeño", "Dilithium-5 grande"])


# Calcular medias
means = [pd.Series(data[key]).mean() for key in data.keys()]

# Superponer las medias en el gráfico como marcadores
for i, mean in enumerate(means, start=1):  # Enumerar desde 1 (índices del gráfico de cajas)
    plt.scatter(i, mean, color='green', marker='^')

# Personalizar el gráfico
plt.title("Comparación de Tiempos Totales de Ejecución entre Versiones de Dilithium")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Dilithium y Tamaño de Firma")

# Mostrar el gráfico
plt.grid(True)
plt.tight_layout()
plt.show()
