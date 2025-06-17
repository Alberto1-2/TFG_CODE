import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Leer los tres archivos CSV
files = ["kyber512_performance2.csv", "kyber768_performance2.csv", "kyber1024_performance2.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de Kyber
data = {"kyber512": [], "kyber768": [], "kyber1024": []}

# Leer y procesar cada archivo CSV
for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Extraer la versión de Kyber y el tiempo total
    for _, row in df.iterrows():
        version = row["Kyber Version"]
        total_time = row["Tiempo Total"]
        
        # Agregar el tiempo total a la lista correspondiente
        data[version].append(total_time)


# Calcular promedios para cada versión
means = [np.mean(data["kyber512"]), np.mean(data["kyber768"]), np.mean(data["kyber1024"])]

# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["kyber512"], data["kyber768"], data["kyber1024"]],
            labels=["kyber512", "kyber768", "kyber1024"])


# Agregar promedios al gráfico como triángulos verdes
for i, mean in enumerate(means, start=1):
    plt.plot(i, mean, marker="^", color="green", markersize=8, label="_nolegend_")

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de Kyber")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Kyber")

# Mostrar el gráfico
plt.grid(True)
plt.show()
