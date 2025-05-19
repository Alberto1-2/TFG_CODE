import pandas as pd
import matplotlib.pyplot as plt

# Nombre del archivo combinado
file = "SPHINCS+.csv"

# Parámetros de las versiones
implementations = [
    ('ref', ['shake', 'sha2'])
    
]
options = ["f", "s"]
sizes = [128, 192, 256]

# Número de iteraciones por combinación de versión
iterations_per_version = 100  # Cambiar al número correcto

# Generar las etiquetas de las versiones
versions = []
for impl, hashes in implementations:
    for h in hashes:
        for opt in options:
            for size in sizes:
                versions.append(f"{impl}-{h}-{size}{opt}")

# Leer el archivo CSV
df = pd.read_csv(file)

# Verificar si el archivo tiene las columnas esperadas
if "Tiempo Total (ms)" not in df.columns:
    raise ValueError(f"El archivo {file} no contiene la columna 'Tiempo Total (ms)'.")

# Asignar etiquetas a cada línea en función de su posición
df['label'] = df.index // iterations_per_version
df['label'] = df['label'].map(lambda x: versions[x % len(versions)])

# Crear un diccionario para almacenar los datos por versión
data = {version: df[df['label'] == version]["Tiempo Total (ms)"].tolist() for version in versions}

# Crear el diagrama de cajas
plt.figure(figsize=(10, 6))
plt.boxplot([data[version] for version in versions],
            labels=versions, showmeans=True)

# Calcular medias
#means = [pd.Series(data[version]).mean() for version in versions]

# Superponer las medias en el gráfico como marcadores
#for i, mean in enumerate(means, start=1):  # Enumerar desde 1 (índices del gráfico de cajas)
#    plt.scatter(i, mean, color='green', marker='^', label='Media' if i == 1 else "")

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución por versión de SPHINCS+")
plt.ylabel("Tiempo total de Ejecución (ms)")
plt.xlabel("Versión de SPHINCS+")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(rotation=45, ha='right')


# Mostrar el gráfico
plt.tight_layout()
plt.show()
