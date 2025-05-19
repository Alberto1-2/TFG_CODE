import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

files = ["sha2-128f-robust_performance.csv", "sha2-128s-robust_performance.csv", "sha2-192f-robust_performance.csv", "sha2-192s-robust_performance.csv", "sha2-256f-robust_performance.csv", "sha2-256s-robust_performance.csv",
         "shake-128f-robust_performanceShake.csv", "shake-128s-robust_performanceShake.csv", "shake-192f-robust_performanceShake.csv", "shake-192s-robust_performanceShake.csv", "shake-256f-robust_performanceShake.csv", "shake-256s-robust_performanceShake.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de Kyber
data = {"sha2-128f-robust": [], "sha2-128s-robust": [], "sha2-192f-robust": [], "sha2-192s-robust": [], "sha2-256f-robust": [], "sha2-256s-robust": [],
        "shake-128f-robust": [], "shake-128s-robust": [], "shake-192f-robust": [], "shake-192s-robust": [], "shake-256f-robust": [], "shake-256s-robust": []}

for file in files:
    df = pd.read_csv(file)
    
    # Extraer la versión de Kyber y el tiempo total
    for _, row in df.iterrows():
        version = row["SPHINCS+ Version"]
        total_time = row["Tiempo Total"]
        
        # Agregar el tiempo total a la lista correspondiente
        data[version].append(total_time)


# Calcular promedios para cada versión
means = [np.mean(data["sha2-128f-robust"]), np.mean(data["sha2-128s-robust"]), np.mean(data["sha2-192f-robust"]), np.mean(data["sha2-192s-robust"]), np.mean(data["sha2-256f-robust"]), np.mean(data["sha2-256s-robust"]),
        np.mean(data["shake-128f-robust"]), np.mean(data["shake-128s-robust"]), np.mean(data["shake-192f-robust"]), np.mean(data["shake-192s-robust"]), np.mean(data["shake-256f-robust"]), np.mean(data["shake-256s-robust"])]
# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["sha2-128f-robust"], data["sha2-128s-robust"], data["sha2-192f-robust"], data["sha2-192s-robust"], data["sha2-256f-robust"], data["sha2-256s-robust"],
             data["shake-128f-robust"], data["shake-128s-robust"], data["shake-192f-robust"], data["shake-192s-robust"], data["shake-256f-robust"], data["shake-256s-robust"]],
            labels=["sha2-128f", "sha2-128s", "sha2-192f", "sha2-192s", "sha2-256f", "sha2-256s",
                    "shake-128f", "shake-128s", "shake-192f", "shake-192s", "shake-256f", "shake-256s"])

# Agregar promedios al gráfico como triángulos verdes
for i, mean in enumerate(means, start=1):
    plt.plot(i, mean, marker="^", color="green", markersize=5, label="_nolegend_")

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de Sphincs+")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Sphincs+")

# Mostrar el gráfico
plt.grid(True)
plt.show()
