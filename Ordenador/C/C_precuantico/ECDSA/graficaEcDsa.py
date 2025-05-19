import pandas as pd
import matplotlib.pyplot as plt

# Crear gráficos
files = ["ecdsa_secp256r1.csv", "ecdsa_secp384r1.csv", "Native_ecdsa256r1.csv", "Native_ecdsa384r1.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de ECDSA
data = {"ecdsa_secp256r1": [], "ecdsa_secp384r1": [], "Native_ecdsa256r1": [], "Native_ecdsa384r1": []}

# Leer y procesar cada archivo CSV
for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Procesar cada fila del archivo
    for _, row in df.iterrows():
        # Crear una clave simple para cada archivo, utilizando solo el nombre del archivo
        if "ecdsa_secp256r1" in file:
            key = "ecdsa_secp256r1"
        elif "ecdsa_secp384r1" in file:
            key = "ecdsa_secp384r1"
        elif "Native_ecdsa256r1" in file:
            key = "Native_ecdsa256r1"
        elif "Native_ecdsa384r1" in file:
            key = "Native_ecdsa384r1"    
        
        # Verificar si la clave existe en el diccionario y agregar el Tiempo Total
        if key in data:
            data[key].append(row["Tiempo Total (ms)"])
        else:
            print(f"Advertencia: Clave '{key}' no encontrada en el diccionario.")

# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["ecdsa_secp256r1"], data["ecdsa_secp384r1"], data["Native_ecdsa256r1"], data["Native_ecdsa384r1"]],
            labels=["ecdsa_secp256r1", "ecdsa_secp384r1", "Native_ecdsa256r1", "Native_ecdsa384r1"],
            showmeans=True, showfliers=True)  # Los puntos salientes se muestran

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de ECDSA")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de ECDSA")

# Mostrar el gráfico
plt.grid(True)
plt.show()
