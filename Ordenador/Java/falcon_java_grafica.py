import pandas as pd
import matplotlib.pyplot as plt

# Nombres de los archivos CSV
files = ["falcon-512_grande_performance.csv", "falcon-512_pequeño_performance.csv", 
         "falcon-1024_grande_performance.csv", "falcon-1024_pequeño_performance.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de Falcon
data = {"falcon-512 grande": [], "falcon-512 pequeño": [], 
        "falcon-1024 grande": [], "falcon-1024 pequeño": []}

# Leer y procesar cada archivo CSV
for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Procesar cada fila del archivo
    for _, row in df.iterrows():
        # Construir la clave combinando la versión y el tamaño del mensaje
        key = f"{row['Falcon Version']} {row['Tamaño Mensaje']}"
        
        # Verificar si la clave existe en el diccionario
        if key in data:
            data[key].append(row["Tiempo Total"])
        else:
            print(f"Advertencia: Clave '{key}' no encontrada en el diccionario.")

# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data["falcon-512 grande"], data["falcon-512 pequeño"], 
             data["falcon-1024 grande"], data["falcon-1024 pequeño"]],
            labels=["falcon-512 grande", "falcon-512 pequeño", 
                    "falcon-1024 grande", "falcon-1024 pequeño"])

# Calcular medias
means = [pd.Series(data[key]).mean() for key in data.keys()]

# Superponer las medias en el gráfico como marcadores
for i, mean in enumerate(means, start=1):  # Enumerar desde 1 (índices del gráfico de cajas)
    plt.scatter(i, mean, color='green', marker='^')
# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de Falcon")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Falcon")

# Mostrar el gráfico
plt.grid(True)
plt.show()
