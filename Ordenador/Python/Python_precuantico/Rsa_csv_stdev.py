import time
import csv
import statistics
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Función para medir el rendimiento de la generación de claves, creación y verificación de firmas
def medir_rendimiento(bits, n_iterations, filename):
    print(f"\nIniciando pruebas para claves RSA de {bits} bits...")

    # Abrir el archivo CSV para escribir los resultados
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Iteración', 'Tiempo Generación de Claves (ms)', 'Tiempo Creación de Firma (ms)', 'Tiempo Verificación de Firma (ms)', 'Tiempo Total (ms)'])

        # Inicializamos las listas para almacenar los tiempos de cada iteración
        tiempos_generacion_claves = []
        tiempos_creacion_firma = []
        tiempos_verificacion_firma = []

        for i in range(n_iterations):
            # 1. Generación de claves RSA
            start_time = time.time()
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=bits,
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
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            end_time = time.time()
            tiempo_creacion_firma_iter = (end_time - start_time) * 1000  # Convertir a milisegundos
            tiempos_creacion_firma.append(tiempo_creacion_firma_iter)

            # 3. Verificación de la firma
            start_time = time.time()
            public_key.verify(
                signature,
                mensaje,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            end_time = time.time()
            tiempo_verificacion_firma_iter = (end_time - start_time) * 1000  # Convertir a milisegundos
            tiempos_verificacion_firma.append(tiempo_verificacion_firma_iter)

            # Escribir los resultados de cada iteración en el archivo CSV
            writer.writerow([i + 1, tiempo_generacion_claves_iter, tiempo_creacion_firma_iter, tiempo_verificacion_firma_iter,
                             tiempo_creacion_firma_iter + tiempo_generacion_claves_iter + tiempo_verificacion_firma_iter])
            
            #print(f"Iteración {i+1} completada.")

        # Calcular los tiempos promedio
        promedio_generacion_claves = sum(tiempos_generacion_claves) / n_iterations
        promedio_creacion_firma = sum(tiempos_creacion_firma) / n_iterations
        promedio_verificacion_firma = sum(tiempos_verificacion_firma) / n_iterations

        # Calcular la desviación estándar
        desviacion_generacion_claves = statistics.stdev(tiempos_generacion_claves)
        desviacion_creacion_firma = statistics.stdev(tiempos_creacion_firma)
        desviacion_verificacion_firma = statistics.stdev(tiempos_verificacion_firma)

        # Mostrar resultados promedio y desviación estándar
        print(f"\nResultados promedio para {n_iterations} iteraciones:")
        print(f"Tiempo de generación de claves: {promedio_generacion_claves:.3f} ms (Desviación estándar: {desviacion_generacion_claves:.3f} ms)")
        print(f"Tiempo de creación de la firma: {promedio_creacion_firma:.3f} ms (Desviación estándar: {desviacion_creacion_firma:.3f} ms)")
        print(f"Tiempo de verificación de la firma: {promedio_verificacion_firma:.3f} ms (Desviación estándar: {desviacion_verificacion_firma:.3f} ms)")
    
    return promedio_generacion_claves, promedio_creacion_firma, promedio_verificacion_firma, desviacion_generacion_claves, desviacion_creacion_firma, desviacion_verificacion_firma

# Probar RSA con claves de 2048 y 4096 bits y escribir los resultados en archivos CSV
medir_rendimiento(2048, 1000, 'rsa_2048.csv')
medir_rendimiento(4096, 1000, 'rsa_4096.csv')
