import pandas as pd
import matplotlib.pyplot as plt

files = ["ecdsa_256.csv", "ecdsa_384.csv"]

data = {"ecdsa_256": [], "ecdsa_384": []}

for file in files:
    df = pd.read_csv(file)
    
    # Procesar cada fila del archivo
    for _, row in df.iterrows():
        # Crear una clave simple para cada archivo, utilizando solo el nombre del archivo
        if "ecdsa_256" in file:
            key = "ecdsa_256"
        elif "ecdsa_384" in file:
            key = "ecdsa_384"
        
        # Verificar si la clave existe en el diccionario y agregar el Tiempo Total
        if key in data:
            data[key].append(row["Tiempo Total (ms)"])
        else:
            print(f"Advertencia: Clave '{key}' no encontrada en el diccionario.")

# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["ecdsa_256"], data["ecdsa_384"]],
            labels=["ecdsa_256", "ecdsa_384"],
            showmeans=True, showfliers=True)  # Los puntos salientes se muestran

plt.title("Comparación de tiempos totales de ejecución entre versiones de ECDSA")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de ECDSA")

# Mostrar el gráfico
plt.grid(True)
plt.show()
