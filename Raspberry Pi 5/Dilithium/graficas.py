import pandas as pd
import matplotlib.pyplot as plt

# Nombres de los archivos CSV
files = ["Dilithium2_REF_results.csv", "Dilithium3_REF_results.csv", "Dilithium5_REF_results.csv",
         "Dilithium2_NEON_results.csv", "Dilithium3_NEON_results.csv", "Dilithium5_NEON_results.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión
data = {"Dilithium2_REF": [], "Dilithium3_REF": [], "Dilithium5_REF": [],
        "Dilithium2_NEON": [], "Dilithium3_NEON": [], "Dilithium5_NEON": []}

for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Verificamos si el archivo tiene las columnas esperadas
    if "Total Time (ms)" in df.columns:
        # Añadimos los tiempos totales de este archivo al diccionario correspondiente
        key = file.split('_')[0] + "_" + file.split('_')[1]  # Crea la clave en formato <dilithiumX_test> o <dilithiumX_neon>
        data[key].extend(df["Total Time (ms)"]) 
    else:
        print(f"Advertencia: El archivo {file} no contiene la columna 'Total Time (ms)'.")

# Crear el diagrama de cajas
plt.figure(figsize=(12, 8))
plt.boxplot([data["Dilithium2_REF"], data["Dilithium3_REF"], data["Dilithium5_REF"],
             data["Dilithium2_NEON"], data["Dilithium3_NEON"], data["Dilithium5_NEON"]],
            labels=["dilithium2", "dilithium3", "dilithium5", "dilithium2_neon", "dilithium3_neon", "dilithium5_neon"])

# Calcular medias
means = [pd.Series(data[key]).mean() for key in data.keys()]

for i, mean in enumerate(means, start=1):
    plt.scatter(i, mean, color='green', marker='^')

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de Dilithium")
plt.ylabel("Tiempo total de Ejecución (ms)")
plt.xlabel("Versión de Dilithium")
plt.legend()

# Mostrar el gráfico
plt.grid(True)
plt.show()
