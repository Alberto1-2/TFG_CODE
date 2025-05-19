import pandas as pd
import matplotlib.pyplot as plt

# Nombres de los archivos CSV de las diferentes versiones de Kyber
files = ["Kyber512_Iteration.csv", 
         "Kyber768_Iteration.csv", 
         "Kyber1024_Iteration.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de Kyber
data = {"Kyber-512": [], "Kyber-768": [], "Kyber-1024": []}

# Leer y procesar cada archivo CSV
for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Imprimir las primeras filas para verificar el contenido
    print(f"Contenido de {file}:")
    print(df.head())  # Imprime las primeras filas del archivo
    
    # Determinar la versión que corresponde al archivo
    if "Kyber512" in file:
        version_key = "Kyber-512"
    elif "Kyber768" in file:
        version_key = "Kyber-768"
    elif "Kyber1024" in file:
        version_key = "Kyber-1024"
    else:
        version_key = None
    
    # Verificar que la clave de versión sea correcta
    if version_key:
        print(f"Procesando {version_key}")
    
    # Agregar los tiempos al diccionario
    #data[version_key].extend(df["TotalTime"])
    # Procesar cada fila del archivo
    for _, row in df.iterrows():
        # Agregar los tiempos en el diccionario, dependiendo del tamaño de la firma
        data[version_key].append(row["TotalTime"])

# Imprimir los datos agregados en el diccionario para verificar
print("\nContenido del diccionario de datos:")
for key, value in data.items():
    print(f"{key}: {len(value)} valores")

# Crear el diagrama de cajas
plt.figure(figsize=(12, 6))
plt.boxplot([data["Kyber-512"], data["Kyber-768"], data["Kyber-1024"]],
            tick_labels=["Kyber-512", "Kyber-768", "Kyber-1024"])

# Calcular medias
means = [pd.Series(data[key]).mean() for key in data.keys()]

# Superponer las medias en el gráfico como marcadores
for i, mean in enumerate(means, start=1):  # Enumerar desde 1 (índices del gráfico de cajas)
    plt.scatter(i, mean, color='green', marker='^')

# Personalizar el gráfico
plt.title("Comparación de Tiempos Totales de Ejecución entre Versiones de Kyber")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Kyber")

# Mostrar el gráfico
plt.grid(True)
plt.show()
