import pandas as pd
import matplotlib.pyplot as plt

files = ["Kyber512_REF_results.csv", "Kyber768_REF_results.csv", "Kyber1024_REF_results.csv", 
         "Kyber512_NEON_results.csv", "Kyber768_NEON_results.csv", "Kyber1024_NEON_results.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión
data = {"kyber512_neon": [], "kyber768_neon": [], "kyber1024_neon": [],
        "kyber512_test": [], "kyber768_test": [], "kyber1024_test": []}

for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    if "Tiempo Total (ms)" in df.columns:
        # Extraer la clave según el nombre del archivo
        if "NEON" in file:
            if "Kyber512" in file:
                key = "kyber512_neon"
            elif "Kyber768" in file:
                key = "kyber768_neon"
            elif "Kyber1024" in file:
                key = "kyber1024_neon"
        elif "REF" in file:
            if "Kyber512" in file:
                key = "kyber512_test"
            elif "Kyber768" in file:
                key = "kyber768_test"
            elif "Kyber1024" in file:
                key = "kyber1024_test"
        else:
            print(f"Advertencia: El archivo {file} no tiene un formato reconocido.")
            continue

        # Agregar los tiempos totales de este archivo al diccionario correspondiente
        data[key].extend(df["Tiempo Total (ms)"])
    else:
        print(f"Advertencia: El archivo {file} no contiene la columna 'Tiempo Total (ms)'.")

# Crear el diagrama de cajas
plt.figure(figsize=(12, 8))
plt.boxplot([data["kyber512_neon"], data["kyber768_neon"], data["kyber1024_neon"],
             data["kyber512_test"], data["kyber768_test"], data["kyber1024_test"]],
            labels=["kyber512_neon", "kyber768_neon", "kyber1024_neon",
                    "kyber512", "kyber768", "kyber1024"])

# Calcular medias
means = [pd.Series(data[key]).mean() for key in data.keys()]

# Superponer las medias en el gráfico como marcadores
for i, mean in enumerate(means, start=1):  # Enumerar desde 1 (índices del gráfico de cajas)
    plt.scatter(i, mean, color='green', marker='^')

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de Kyber")
plt.ylabel("Tiempo total de Ejecución (ms)")
plt.xlabel("Versión de Kyber")
plt.grid(True)

# Mostrar el gráfico
plt.show()
