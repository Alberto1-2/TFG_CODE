import pandas as pd
import matplotlib.pyplot as plt

files = ["rsa_2048.csv", "rsa_4096.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de Falcon
data = {"rsa_2048": [], "rsa_4096": []}

for file in files:
    df = pd.read_csv(file)
    
    # Procesar cada fila del archivo
    for _, row in df.iterrows():
        # Crear una clave simple para cada archivo, utilizando solo el nombre del archivo
        if "rsa_2048" in file:
            key = "rsa_2048"
        elif "rsa_4096" in file:
            key = "rsa_4096"
        
        # Verificar si la clave existe en el diccionario y agregamos el Tiempo Total
        if key in data:
            data[key].append(row["Tiempo Total (ms)"])
        else:
            print(f"Advertencia: Clave '{key}' no encontrada en el diccionario.")

# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["rsa_2048"], data["rsa_4096"]],
            labels=["rsa_2048", "rsa_4096"],
                    showmeans=True, showfliers=True)

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de Rsa")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Rsa")

# Mostrar el gráfico
plt.grid(True)
plt.show()
