import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

files = ["Dilithium2_performance.csv", "Dilithium3_performance.csv", "Dilithium5_performance.csv"]

# Creamos un diccionario para almacenar los tiempos totales por versión de Kyber
data = {"Dilithium2": [], "Dilithium3": [], "Dilithium5": []}

for file in files:
    df = pd.read_csv(file)
    
    # Extraer la versión de Kyber y el tiempo total
    for _, row in df.iterrows():
        version = row["Dilithium Version"]
        total_time = row["Tiempo Total"]
        
        # Agregar el tiempo total a la lista correspondiente
        data[version].append(total_time)

# Calcular promedios para cada versión
means = [np.mean(data["Dilithium2"]), np.mean(data["Dilithium3"]),
         np.mean(data["Dilithium5"])]
# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["Dilithium2"], data["Dilithium3"], data["Dilithium5"]],
            labels=["Dilithium2", "Dilithium3", "Dilithium5"])


for i, mean in enumerate(means, start=1):
    plt.plot(i, mean, marker="^", color="green", markersize=8, label="_nolegend_")

plt.title("Comparación de tiempos totales de ejecución entre versiones de Dilithium")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Dilithium")


plt.grid(True)
plt.show()
