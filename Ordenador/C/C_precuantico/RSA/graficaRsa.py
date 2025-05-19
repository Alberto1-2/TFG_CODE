import pandas as pd
import matplotlib.pyplot as plt

# Crear gráficos
files = ["rsa_2048.csv", "rsa_4096.csv", "Native_rsa2048.csv", "Native_rsa4096.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de ECDSA
data = {"rsa_2048": [], "rsa_4096": [], "Native_rsa2048": [], "Native_rsa4096": []}

# Leer y procesar cada archivo CSV
for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Procesar cada fila del archivo
    for _, row in df.iterrows():
        # Crear una clave simple para cada archivo, utilizando solo el nombre del archivo
        if "rsa_2048" in file:
            key = "rsa_2048"
        elif "rsa_4096" in file:
            key = "rsa_4096"
        elif "Native_rsa2048" in file:
            key = "Native_rsa2048"
        elif "Native_rsa4096" in file:
            key = "Native_rsa4096"    
        
        # Verificar si la clave existe en el diccionario y agregar el Tiempo Total
        if key in data:
            data[key].append(row["Tiempo Total (ms)"])
        else:
            print(f"Advertencia: Clave '{key}' no encontrada en el diccionario.")

# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["rsa_2048"], data["rsa_4096"], data["Native_rsa2048"], data["Native_rsa4096"]],
            labels=["rsa_2048", "rsa_4096", "Native_rsa2048", "Native_rsa4096"],
            showmeans=True, showfliers=True)  # Los puntos salientes se muestran

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de RSA")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de RSA")

# Mostrar el gráfico
plt.grid(True)
plt.show()
