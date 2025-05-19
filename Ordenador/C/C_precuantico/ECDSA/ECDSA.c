#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include <openssl/ec.h>
#include <openssl/ecdsa.h>
#include <openssl/objects.h>
#include <openssl/err.h>
#include <openssl/sha.h>

void medir_rendimiento(const char *curve_name, int nid, int n_iterations, const char *filename);
double calcular_promedio(double *tiempos, int n);
double calcular_desviacion_estandar(double *tiempos, int n, double promedio);

int main() {
    // Pruebas para secp256r1 y secp384r1
    medir_rendimiento("secp256r1", NID_X9_62_prime256v1, 1000, "ecdsa_secp256r1.csv");
    medir_rendimiento("secp384r1", NID_secp384r1, 1000, "ecdsa_secp384r1.csv");
    return 0;
}

void medir_rendimiento(const char *curve_name, int nid, int n_iterations, const char *filename) {
    printf("\nIniciando pruebas para la curva %s...\n", curve_name);

    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("Error al abrir el archivo");
        return;
    }
    fprintf(file, "Iteración,Tiempo Generación Claves (ms),Tiempo Creación Firma (ms),Tiempo Verificación Firma (ms),Tiempo Total (ms)\n");

    double tiempos_generacion[n_iterations];
    double tiempos_firma[n_iterations];
    double tiempos_verificacion[n_iterations];
    double tiempos_totales[n_iterations];

    /// Warmup para evitar la carga de recursos inicial altere la gráfica
    EC_KEY *key_warmup = NULL;
    unsigned char hash_warmup[SHA256_DIGEST_LENGTH];
    unsigned char *signature_warmup = NULL;
    unsigned int sig_len_warmup = 0;
    // Generar claves
    key_warmup = EC_KEY_new_by_curve_name(nid);
    if (!key_warmup || !EC_KEY_generate_key(key_warmup)) {
        fprintf(stderr, "Error al generar claves\n");
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }
    // Crear mensaje hash
    const char *mensaje_warmup = "Este es un mensaje de prueba para firmar.";
    SHA256((unsigned char *)mensaje_warmup, strlen(mensaje_warmup), hash_warmup);

    // Crear firma
    sig_len_warmup = ECDSA_size(key_warmup); // Usamos el tam de clave de 2048 o 4096 bits
    signature_warmup = malloc(sig_len_warmup);
    if (!signature_warmup || !ECDSA_sign(0, hash_warmup, SHA256_DIGEST_LENGTH, signature_warmup, &sig_len_warmup, key_warmup)) {
        fprintf(stderr, "Error al firmar\n");
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }
    // Verificamos la firma
    int verificacion_wup = ECDSA_verify(0, hash_warmup, SHA256_DIGEST_LENGTH, signature_warmup, sig_len_warmup, key_warmup);

    if (verificacion_wup != 1) {
        fprintf(stderr, "Advertencia: Firma no válida");
    }
    // Ejecución principal de ECDSA
    for (int i = 0; i < n_iterations; i++) {
        clock_t start, end;
        EC_KEY *key = NULL;
        unsigned char hash[SHA256_DIGEST_LENGTH];
        unsigned char *signature = NULL;
        unsigned int sig_len = 0;
        
        // Generar claves
        start = clock();
        key = EC_KEY_new_by_curve_name(nid);
        if (!key || !EC_KEY_generate_key(key)) {
            fprintf(stderr, "Error al generar claves\n");
            ERR_print_errors_fp(stderr);
            goto cleanup;
        }
        end = clock();
        double tiempo_generacion = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;
        tiempos_generacion[i] = tiempo_generacion;

        // Crear mensaje hash
        const char *mensaje = "Este es un mensaje de prueba para firmar.";
        SHA256((unsigned char *)mensaje, strlen(mensaje), hash);

        // Crear firma
        start = clock();
        sig_len = ECDSA_size(key);
        signature = malloc(sig_len);
        if (!signature || !ECDSA_sign(0, hash, SHA256_DIGEST_LENGTH, signature, &sig_len, key)) {
            fprintf(stderr, "Error al firmar\n");
            ERR_print_errors_fp(stderr);
            goto cleanup;
        }
        end = clock();
        double tiempo_firma = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;
        tiempos_firma[i] = tiempo_firma;

        // Verificar firma
        start = clock();
        int verificacion = ECDSA_verify(0, hash, SHA256_DIGEST_LENGTH, signature, sig_len, key);
        end = clock();
        double tiempo_verificacion = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;
        tiempos_verificacion[i] = tiempo_verificacion;

        if (verificacion != 1) {
            fprintf(stderr, "Advertencia: Firma no válida en la iteración %d\n", i + 1);
        }

        // Tiempo total
        double tiempo_total = tiempo_generacion + tiempo_firma + tiempo_verificacion;
        tiempos_totales[i] = tiempo_total;

        // Escribir resultados en el archivo
        fprintf(file, "%d,%.3f,%.3f,%.3f,%.3f\n", i + 1, tiempo_generacion, tiempo_firma, tiempo_verificacion, tiempo_total);
        printf("Iteración %d completada.\n", i + 1);

    cleanup:
        if (key) EC_KEY_free(key);
        if (signature) free(signature);
    }

    // Calcular y mostrar resultados
    double promedio_generacion = calcular_promedio(tiempos_generacion, n_iterations);
    double promedio_firma = calcular_promedio(tiempos_firma, n_iterations);
    double promedio_verificacion = calcular_promedio(tiempos_verificacion, n_iterations);
    double promedio_total = calcular_promedio(tiempos_totales, n_iterations);

    double desviacion_generacion = calcular_desviacion_estandar(tiempos_generacion, n_iterations, promedio_generacion);
    double desviacion_firma = calcular_desviacion_estandar(tiempos_firma, n_iterations, promedio_firma);
    double desviacion_verificacion = calcular_desviacion_estandar(tiempos_verificacion, n_iterations, promedio_verificacion);
    double desviacion_total = calcular_desviacion_estandar(tiempos_totales, n_iterations, promedio_total);

    printf("\nResultados promedio para %d iteraciones:\n", n_iterations);
    printf("Tiempo de generación de claves: %.3f ms (Desviación estándar: %.3f ms)\n", promedio_generacion, desviacion_generacion);
    printf("Tiempo de creación de la firma: %.3f ms (Desviación estándar: %.3f ms)\n", promedio_firma, desviacion_firma);
    printf("Tiempo de verificación de la firma: %.3f ms (Desviación estándar: %.3f ms)\n", promedio_verificacion, desviacion_verificacion);
    printf("Tiempo total: %.3f ms (Desviación estándar: %.3f ms)\n", promedio_total, desviacion_total);

    fclose(file);
}

double calcular_promedio(double *tiempos, int n) {
    double suma = 0.0;
    for (int i = 0; i < n; i++) {
        suma += tiempos[i];
    }
    return suma / n;
}

double calcular_desviacion_estandar(double *tiempos, int n, double promedio) {
    double suma = 0.0;
    for (int i = 0; i < n; i++) {
        suma += (tiempos[i] - promedio) * (tiempos[i] - promedio);
    }
    return sqrt(suma / (n - 1));
}
