import os
import time
import importlib
import statistics
import matplotlib.pyplot as plt

# Parámetros y configuraciones de SPHINCS+
paramsets = [
    'shake_128s', 'shake_128f', 'shake_192s', 'shake_192f', 'shake_256s', 'shake_256f',
    'sha2_128s', 'sha2_128f', 'sha2_192s', 'sha2_192f', 'sha2_256s', 'sha2_256f',
]

# Crear las instancias importadas junto a sus nombres
instances = [(importlib.import_module(f'pyspx.{paramset}'), paramset) for paramset in paramsets]

# Número de pruebas para promediar tiempos
NTESTS = 2

# Resultados globales
global_results = {}

def test_performance(pyspx, paramset_name):
    """Realiza las pruebas de rendimiento para la configuración dada."""
    # Listas para registrar tiempos
    keygen_times = []
    sign_times = []
    verify_times = []
    total_times = []

    for i in range(1, NTESTS + 1):
        print(f"Prueba {i} para {paramset_name}")

        # Generar una semilla aleatoria para la generación de claves
        seed = os.urandom(pyspx.crypto_sign_SEEDBYTES)
        message = os.urandom(32)  # Mensaje de prueba de 32 bytes

        # Medir el tiempo de generación de claves
        start = time.time()
        public_key, secret_key = pyspx.generate_keypair(seed)
        end = time.time()
        keygen_time = end - start
        keygen_times.append(keygen_time)

        # Medir el tiempo de firma
        start = time.time()
        signature = pyspx.sign(message, secret_key)
        end = time.time()
        sign_time = end - start
        sign_times.append(sign_time)

        # Medir el tiempo de verificación
        start = time.time()
        result = pyspx.verify(message, signature, public_key)
        end = time.time()
        verify_time = end - start
        verify_times.append(verify_time)

        # Registrar tiempo total
        total_times.append((keygen_time + sign_time + verify_time) * 1000)  # Convertir a ms

        # Verificar la validez de la firma
        assert result, "Firma no válida en la verificación"

    # Calcular estadísticas
    avg_keygen = statistics.mean(keygen_times) * 1000
    std_keygen = statistics.stdev(keygen_times) * 1000
    avg_sign = statistics.mean(sign_times) * 1000
    std_sign = statistics.stdev(sign_times) * 1000
    avg_verify = statistics.mean(verify_times) * 1000
    std_verify = statistics.stdev(verify_times) * 1000

    # Guardar tiempos totales en el diccionario global
    global_results[paramset_name] = total_times

    # Imprimir resultados
    print(f"Resultados de rendimiento para {paramset_name}:")
    print(f"Tiempo promedio de generación de claves: {avg_keygen:.4f} ± {std_keygen:.4f} ms")
    print(f"Tiempo promedio de firma: {avg_sign:.4f} ± {std_sign:.4f} ms")
    print(f"Tiempo promedio de verificación: {avg_verify:.4f} ± {std_verify:.4f} ms\n")

def plot_global_results():
    """Genera un gráfico de caja para todos los tipos de configuraciones."""
    print("Generando el gráfico de resultados globales...")
    
    # Preparar datos para el diagrama
    labels = list(global_results.keys())
    data = [global_results[param] for param in labels]

    # Calcular medias para cada configuración
    means = [statistics.mean(times) for times in data]

    # Crear gráfico
    plt.figure(figsize=(12, 8))
    box = plt.boxplot(data, labels=labels, vert=True, patch_artist=True)

     # Superponer las medias como triángulos verdes
    for i, mean in enumerate(means, start=1):  # Enumeración de 1 porque el gráfico de cajas indexa desde 1
        plt.scatter(i, mean, color='green', marker='^', label="Media" if i == 1 else "")  # Etiqueta solo para el primero


    plt.title("Rendimiento de SPHINCS+ (Tiempo Total por Configuración)")
    plt.ylabel("Tiempo total (ms)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Guardar y mostrar el gráfico
    plt.savefig('global_performance_boxplot.png')
    plt.show()

def main():
    """Ejecuta todas las pruebas y genera el gráfico de resultados."""
    for pyspx, paramset_name in instances:
        try:
            test_performance(pyspx, paramset_name)
        except Exception as e:
            print(f"Error durante la prueba para {paramset_name}: {e}")

    plot_global_results()

if __name__ == "__main__":
    main()
