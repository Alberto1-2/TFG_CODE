import pandas as pd
import matplotlib.pyplot as plt

# Nombres de los archivos CSV
files = ["PI5dilithium2_test_results.csv", "PI5dilithium3_test_results.csv", "PI5dilithium5_test_results.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión
data = {"PI5dilithium2_test": [], "PI5dilithium3_test": [], "PI5dilithium5_test": []}

# Leer y procesar cada archivo CSV
for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Verificar si el archivo tiene las columnas esperadas
    if "Total Time (ms)" in df.columns:
        # Agregar los tiempos totales de este archivo al diccionario correspondiente
        # Usar el nombre del archivo (sin la extensión) como la clave
        key = file.split('_')[0] + "_" + file.split('_')[1]  # Crear la clave en formato <dilithiumX_test> o <dilithiumX_avx>
        data[key].extend(df["Total Time (ms)"])  # Agregar los tiempos totales del archivo
    else:
        print(f"Advertencia: El archivo {file} no contiene la columna 'Total Time (ms)'.")

# Crear el diagrama de cajas
plt.figure(figsize=(12, 8))
plt.boxplot([data["PI5dilithium2_test"], data["PI5dilithium3_test"], data["PI5dilithium5_test"]],
            labels=["dilithium2", "dilithium3", "dilithium5"])

# Calcular medias
means = [pd.Series(data[key]).mean() for key in data.keys()]

# Superponer las medias en el gráfico como marcadores
for i, mean in enumerate(means, start=1):  # Enumerar desde 1 (índices del gráfico de cajas)
    plt.scatter(i, mean, color='green', marker='^')

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de Dilithium")
plt.ylabel("Tiempo total de Ejecución (ms)")
plt.xlabel("Versión de Dilithium")
plt.legend()

# Mostrar el gráfico
plt.grid(True)
plt.show()
