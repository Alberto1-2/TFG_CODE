import falcon
import time
import statistics
import matplotlib.pyplot as plt

# Función para medir el rendimiento de Falcon
def medir_rendimiento(tamaño_mensaje, n, repeticiones):
    tiempos_generacion_claves = []
    tiempos_firma = []
    tiempos_verificacion = []
    tiempos_totales = []  # lista para almacenar el tiempo total
    resultados_verificacion = []

    i = 1

    for _ in range(repeticiones):
        #print("Iteración ", i)
        # Generación de la clave privada y la clave pública
        inicio_generacion_claves = time.time()
        private_key = falcon.SecretKey(n)  # Generar clave privada
        public_key = falcon.PublicKey(private_key)  # Derivar clave pública
        tiempo_claves = time.time() - inicio_generacion_claves
        tiempos_generacion_claves.append(tiempo_claves)

        # Crear un mensaje de prueba
        msg = bytes(tamaño_mensaje)  # Mensaje de tamaño variable

        # Firmar el mensaje
        inicio_firma = time.time()
        sig = private_key.sign(msg)
        tiempo_firma = (time.time() - inicio_firma) * 1000
        tiempos_firma.append(tiempo_firma)

        # Verificar la firma
        inicio_verificacion = time.time()
        res = public_key.verify(msg, sig)  # Usar clave pública para verificar
        tiempo_verif = (time.time() - inicio_verificacion) * 1000
        tiempos_verificacion.append(tiempo_verif)

        # Calcular el tiempo total
        tiempo_total = tiempo_claves + (tiempo_firma / 1000) + (tiempo_verif / 1000)
        tiempos_totales.append(tiempo_total)

        resultados_verificacion.append(res)

        i +=1

    # Promediar los tiempos
    tiempo_generacion_claves = sum(tiempos_generacion_claves) / repeticiones
    tiempo_firma = sum(tiempos_firma) / repeticiones
    tiempo_verificacion = sum(tiempos_verificacion) / repeticiones
    tiempo_total_promedio = sum(tiempos_totales) / repeticiones
    firma_valida = all(resultados_verificacion)

    # Calcular desviaciones estándar
    desv_gen_claves = statistics.stdev(tiempos_generacion_claves)
    desv_firma = statistics.stdev(tiempos_firma)
    desv_verificacion = statistics.stdev(tiempos_verificacion)
    desv_total = statistics.stdev(tiempos_totales)

    return (tiempo_generacion_claves, desv_gen_claves,
            tiempo_firma, desv_firma,
            tiempo_verificacion, desv_verificacion,
            tiempo_total_promedio, desv_total,
            firma_valida, tiempos_generacion_claves, tiempos_firma, tiempos_verificacion, tiempos_totales)

# Pruebas con diferentes tamaños de mensaje
small_msg = b"Pruebas de Falcon en python TFG"  # Mensaje pequeño
large_msg = b"A" * 10000  # Mensaje grande (10,000 bytes)
tamaños = [small_msg, large_msg]
resultados = []

version = [256, 512, 1024]

for tamaño in tamaños:
    for v in version:
        (tiempo_gen_claves, desv_gen_claves,
         tiempo_firma, desv_firma,
         tiempo_verif, desv_verif,
         tiempo_total_prom, desv_total,
         resultado, tiempos_claves, tiempos_firma, tiempos_verif, tiempos_totales) = medir_rendimiento(len(tamaño), v, 3)

        resultados.append({
            "Tipo_version": v,
            "tamaño": len(tamaño),
            "tiempo_generacion_claves": tiempo_gen_claves,
            "desv_gen_claves": desv_gen_claves,
            "tiempo_firma": tiempo_firma,
            "desv_firma": desv_firma,
            "tiempo_verificacion": tiempo_verif,
            "desv_verif": desv_verif,
            "tiempo_total": tiempo_total_prom,
            "desv_total": desv_total,
            "firma_valida": resultado,
            "tiempos_claves": tiempos_claves,
            "tiempos_firma": tiempos_firma,
            "tiempos_verif": tiempos_verif,
            "tiempos_totales": tiempos_totales  # Agregar tiempos totales
        })

# Mostrar resultados
for res in resultados:
    print(f"Tipo version: {res['Tipo_version']}")
    print(f"Tamaño de mensaje: {res['tamaño']} bytes")
    print(f"Tiempo promedio de generación de claves: {res['tiempo_generacion_claves']:.4f} segundos (±{res['desv_gen_claves']:.4f})")
    print(f"Tiempo promedio de firma: {res['tiempo_firma']:.4f} milisegundos (±{res['desv_firma']:.4f})")
    print(f"Tiempo promedio de verificación: {res['tiempo_verificacion']:.4f} milisegundos (±{res['desv_verif']:.4f})")
    print(f"Firma válida en todas las pruebas: {res['firma_valida']}\n")

# Crear un diagrama de cajas para el tiempo total
data_totales = [res['tiempos_totales'] for res in resultados]
labels_totales = [f"V{res['Tipo_version']}-{res['tamaño']}" for res in resultados]

plt.figure(figsize=(10, 6))
plt.boxplot(data_totales, labels=labels_totales, showmeans=True)
plt.title("Tiempo Total de Ejecución")
plt.ylabel("Tiempo Total (s)")
plt.xlabel("Configuraciones")
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.show()
