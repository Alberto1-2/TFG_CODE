import pandas as pd
import matplotlib.pyplot as plt

file = "SPHINCS+_NATIVE.csv"

# Parámetros de las versiones
implementations = [
    ('ref', ['shake', 'sha2'])
    
]
options = ["f", "s"]
sizes = [128, 192, 256]


iterations_per_version = 70  # Cambiar según número de iteraciones ejecutadas

# Generar las etiquetas de las versiones
versions = []
for impl, hashes in implementations:
    for h in hashes:
        for opt in options:
            for size in sizes:
                versions.append(f"{impl}-{h}-{size}{opt}")

df = pd.read_csv(file)

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

# Personalizar el gráfico
plt.title("Comparación de tiempos totales de ejecución por versión de SPHINCS+")
plt.ylabel("Tiempo total de Ejecución (ms)")
plt.xlabel("Versión de SPHINCS+")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(rotation=45, ha='right')


# Mostrar el gráfico
plt.tight_layout()
plt.show()
