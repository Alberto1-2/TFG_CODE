import time
import csv
import statistics
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import pandas as pd
import matplotlib.pyplot as plt

# Función para medir el rendimiento de la generación de claves, creación y verificación de firmas
def medir_rendimiento(bits, n_iterations, filename):
    print(f"\nIniciando pruebas para claves ECDSA de {bits} bits...")

    # Abrir el archivo CSV para escribir los resultados
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Iteración', 'Tiempo Generación de Claves (ms)', 'Tiempo Creación de Firma (ms)', 'Tiempo Verificación de Firma (ms)', 'Tiempo Total (ms)'])

        # Inicializamos las listas para almacenar los tiempos de cada iteración
        tiempos_generacion_claves = []
        tiempos_creacion_firma = []
        tiempos_verificacion_firma = []
        tiempos_totales = []

        # Ejecución de warmup para evitar la distorsión de las gráficas
        # 1. Generación de las claves de ECDSA
        private_key = ec.generate_private_key(
            ec.SECP256R1() if bits == 256 else ec.SECP384R1(), 
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # 2. Creación de una firma
        mensaje = b"Este es un mensaje de prueba para firmar."
        signature = private_key.sign(
            mensaje,
            ec.ECDSA(hashes.SHA256())  # Especificar el algoritmo ECDSA para la firma
        )

        # 3. Verificación de la firma
        public_key.verify(
            signature,
            mensaje,
            ec.ECDSA(hashes.SHA256())  # Especificar el algoritmo ECDSA para la verificación
        )

        for i in range(n_iterations):
            # 1. Generación de claves ECDSA
            start_time = time.time()
            private_key = ec.generate_private_key(
                ec.SECP256R1() if bits == 256 else ec.SECP384R1(), 
                backend=default_backend()
            )
            public_key = private_key.public_key()
            end_time = time.time()
            tiempo_generacion_claves_iter = (end_time - start_time) * 1000  # Convertir a milisegundos
            tiempos_generacion_claves.append(tiempo_generacion_claves_iter)

            # 2. Creación de una firma
            mensaje = b"Este es un mensaje de prueba para firmar."
            start_time = time.time()
            signature = private_key.sign(
                mensaje,
                ec.ECDSA(hashes.SHA256())  # Especificar el algoritmo ECDSA para la firma
            )
            end_time = time.time()
            tiempo_creacion_firma_iter = (end_time - start_time) * 1000  # Convertir a milisegundos
            tiempos_creacion_firma.append(tiempo_creacion_firma_iter)

            # 3. Verificación de la firma
            start_time = time.time()
            public_key.verify(
                signature,
                mensaje,
                ec.ECDSA(hashes.SHA256())  # Especificar el algoritmo ECDSA para la verificación
            )
            end_time = time.time()
            tiempo_verificacion_firma_iter = (end_time - start_time) * 1000  # Convertir a milisegundos
            tiempos_verificacion_firma.append(tiempo_verificacion_firma_iter)

            # Calcular el tiempo total (suma de todos los tiempos)
            tiempo_total_iter = tiempo_generacion_claves_iter + tiempo_creacion_firma_iter + tiempo_verificacion_firma_iter
            tiempos_totales.append(tiempo_total_iter)

            # Escribir los resultados de cada iteración en el archivo CSV
            writer.writerow([i + 1, tiempo_generacion_claves_iter, tiempo_creacion_firma_iter, tiempo_verificacion_firma_iter, tiempo_total_iter])
            
            #print(f"Iteración {i+1} completada.")

        # Calcular los tiempos promedio
        promedio_generacion_claves = sum(tiempos_generacion_claves) / n_iterations
        promedio_creacion_firma = sum(tiempos_creacion_firma) / n_iterations
        promedio_verificacion_firma = sum(tiempos_verificacion_firma) / n_iterations
        promedio_total = sum(tiempos_totales) / n_iterations

        # Calcular la desviación estándar
        desviacion_generacion_claves = statistics.stdev(tiempos_generacion_claves)
        desviacion_creacion_firma = statistics.stdev(tiempos_creacion_firma)
        desviacion_verificacion_firma = statistics.stdev(tiempos_verificacion_firma)
        desviacion_total = statistics.stdev(tiempos_totales)

        # Mostrar resultados promedio y desviación estándar
        print(f"\nResultados promedio para {n_iterations} iteraciones:")
        print(f"Tiempo de generación de claves: {promedio_generacion_claves:.3f} ms (Desviación estándar: {desviacion_generacion_claves:.3f} ms)")
        print(f"Tiempo de creación de la firma: {promedio_creacion_firma:.3f} ms (Desviación estándar: {desviacion_creacion_firma:.3f} ms)")
        print(f"Tiempo de verificación de la firma: {promedio_verificacion_firma:.3f} ms (Desviación estándar: {desviacion_verificacion_firma:.3f} ms)")
        print(f"Tiempo total de ejecución: {promedio_total:.3f} ms (Desviación estándar: {desviacion_total:.3f} ms)")

    return promedio_generacion_claves, promedio_creacion_firma, promedio_verificacion_firma, desviacion_generacion_claves, desviacion_creacion_firma, desviacion_verificacion_firma, promedio_total, desviacion_total

# Probar ECDSA con claves de 256 y 384 bits y escribir los resultados en archivos CSV
medir_rendimiento(256, 1000, 'ecdsa_256.csv')
medir_rendimiento(384, 1000, 'ecdsa_384.csv')
