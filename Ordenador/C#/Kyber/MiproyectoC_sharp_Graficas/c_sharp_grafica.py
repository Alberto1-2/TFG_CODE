import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

files = ["kyber512_performance.csv", "kyber768_performance.csv", "kyber1024_performance.csv"]

data = {"kyber512": [], "kyber768": [], "kyber1024": []}

# Leer y procesar cada archivo CSV
for file in files:
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


for i, mean in enumerate(means, start=1):
    plt.plot(i, mean, marker="^", color="green", markersize=8, label="_nolegend_")

plt.title("Comparación de tiempos totales de ejecución entre versiones de Kyber")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Kyber")

plt.grid(True)
plt.show()
