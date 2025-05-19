import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

files = ["Falcon512_grande_performance.csv", "Falcon512_pequeño_performance.csv", 
         "Falcon1024_grande_performance.csv", "Falcon1024_pequeño_performance.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de Falcon
data = {"Falcon512_grande": [], "Falcon512_pequeño": [], 
        "Falcon1024_grande": [], "Falcon1024_pequeño": []}

for file in files:
    df = pd.read_csv(file)
    
    for _, row in df.iterrows():
        # Construir la clave combinando la versión y el tamaño del mensaje
        key = f"{row['Falcon Version']}_{row['Tamaño Mensaje']}"
        
        # Verificamos que la clave esté disponible
        if key in data:
            data[key].append(row["Tiempo Total"])
        else:
            print(f"Advertencia: Clave '{key}' no encontrada en el diccionario.")

# Calcular promedios para cada versión
means = [np.mean(data["Falcon512_grande"]), np.mean(data["Falcon512_pequeño"]),
         np.mean(data["Falcon1024_grande"]), np.mean(data["Falcon1024_pequeño"])]

# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["Falcon512_grande"], data["Falcon512_pequeño"], 
             data["Falcon1024_grande"], data["Falcon1024_pequeño"]],
            labels=["Falcon512_grande", "Falcon512_pequeño", 
                    "Falcon1024_grande", "Falcon1024_pequeño"])

for i, mean in enumerate(means, start=1):
    plt.plot(i, mean, marker="^", color="green", markersize=8, label="_nolegend_")

plt.title("Comparación de tiempos totales de ejecución entre versiones de Falcon")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Falcon")

# Mostrar el gráfico
plt.grid(True)
plt.show()
