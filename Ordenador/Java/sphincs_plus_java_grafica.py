import pandas as pd
import matplotlib.pyplot as plt

# Nombres de los archivos CSV
files = ["sphincsplus_iter_SHA-2_128-bit,_robust_10000bytes.csv", "sphincsplus_iter_SHA-2_128-bit,_standard,_robust_10000bytes.csv", 
         "sphincsplus_iter_SHA-2_192-bit,_robust_10000bytes.csv", "sphincsplus_iter_SHA-2_192-bit,_standard,_robust_10000bytes.csv",
         "sphincsplus_iter_SHA-2_256-bit,_robust_10000bytes.csv", "sphincsplus_iter_SHA-2_256-bit,_standard,_robust_10000bytes.csv",
         "sphincsplus_iter_SHAKE-128,_robust_10000bytes.csv", "sphincsplus_iter_SHAKE-128,_standard,_robust_10000bytes.csv",
         "sphincsplus_iter_SHAKE-192,_robust_10000bytes.csv", "sphincsplus_iter_SHAKE-192,_standard,_robust_10000bytes.csv",
         "sphincsplus_iter_SHAKE-256,_robust_10000bytes.csv", "sphincsplus_iter_SHAKE-256,_standard,_robust_10000bytes.csv"]

# Crear un diccionario para almacenar los tiempos totales por versión de Falcon
data = {"SHA-2 128-bit, robust": [], "SHA-2 128-bit, standard, robust": [], 
        "SHA-2 192-bit, robust": [], "SHA-2 192-bit, standard, robust": [],
        "SHA-2 256-bit, robust": [], "SHA-2 256-bit, standard, robust": [], 
        "SHAKE-128, robust": [], "SHAKE-128, standard, robust": [],
        "SHAKE-192, robust": [], "SHAKE-192, standard, robust": [],
        "SHAKE-256, robust": [], "SHAKE-256, standard, robust": []}

# Leer y procesar cada archivo CSV
for file in files:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Procesar cada fila del archivo
    for _, row in df.iterrows():
        # Construir la clave combinando la versión y el tamaño del mensaje
        key = row['Tipo']
        
        # Verificar si la clave existe en el diccionario
        if key in data:
            data[key].append(row["Tiempo Total"])
        else:
            print(f"Advertencia: Clave '{key}' no encontrada en el diccionario.")



# Crear el diagrama de cajas
plt.figure(figsize=(20, 12))
plt.boxplot([data["SHA-2 128-bit, robust"], data["SHA-2 128-bit, standard, robust"], 
             data["SHA-2 192-bit, robust"], data["SHA-2 192-bit, standard, robust"],
             data["SHA-2 256-bit, robust"], data["SHA-2 256-bit, standard, robust"], 
             data["SHAKE-128, robust"], data["SHAKE-128, standard, robust"],
             data["SHAKE-192, robust"], data["SHAKE-192, standard, robust"],
             data["SHAKE-256, robust"], data["SHAKE-256, standard, robust"]],
            labels=["SHA-2 128f", "SHA-2 128st", 
                    "SHA-2 192f", "SHA-2 192st",
                    "SHA-2 256f", "SHA-2 256st", 
                    "SHAKE-128f", "SHAKE-128st",
                    "SHAKE-192f", "SHAKE-192st",
                    "SHAKE-256f", "SHAKE-256st"])


# Calcular medias
means = [pd.Series(data[key]).mean() for key in data.keys()]

# Superponer las medias en el gráfico como marcadores
for i, mean in enumerate(means, start=1):  # Enumerar desde 1 (índices del gráfico de cajas)
    plt.scatter(i, mean, color='green', marker='^')

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución entre versiones de Sphincs+")
plt.ylabel("Tiempo Total de Ejecución (ms)")
plt.xlabel("Versión de Sphincs+")

# Mostrar el gráfico
plt.grid(True)
plt.show()
