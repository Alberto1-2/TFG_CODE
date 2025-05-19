#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define MESSAGE "Este es un mensaje de prueba para firmar."

// Estructura para almacenar resultados de tiempos
typedef struct {
    double gen_key;
    double sign;
    double verify;
    double total;
} Timing;

// Funciones auxiliares
double calculate_average(double *data, int size);
double calculate_stddev(double *data, int size, double mean);
double get_time_in_ms();
void log_results_to_csv(const char *filename, Timing *results, int n_iterations);

// Función principal para las pruebas
void run_rsa_benchmark(int bits, int n_iterations, const char *filename) {
    printf("\nIniciando pruebas para claves RSA de %d bits...\n", bits);

    // Almacenar los tiempos de cada iteración
    Timing *timings = malloc(sizeof(Timing) * n_iterations);
    if (!timings) {
        fprintf(stderr, "Error al asignar memoria.\n");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < n_iterations; i++) {
        double start, end;
        RSA *rsa = NULL;
        BIGNUM *e = BN_new();
        if (!e || !BN_set_word(e, RSA_F4)) {
            fprintf(stderr, "Error al configurar exponente RSA.\n");
            exit(EXIT_FAILURE);
        }

        // Generación de claves RSA
        start = get_time_in_ms();
        rsa = RSA_new();
        if (!RSA_generate_key_ex(rsa, bits, e, NULL)) {
            fprintf(stderr, "Error al generar claves RSA: %s\n", ERR_error_string(ERR_get_error(), NULL));
            exit(EXIT_FAILURE);
        }
        end = get_time_in_ms();
        timings[i].gen_key = end - start;

        // Asignar memoria para la firma después de inicializar rsa
        unsigned char *signature = malloc(RSA_size(rsa));
        if (!signature) {
            fprintf(stderr, "Error al asignar memoria para la firma.\n");
            exit(EXIT_FAILURE);
        }

        unsigned char hash[SHA256_DIGEST_LENGTH];
        unsigned int sig_len = 0;

        // Crear el hash del mensaje
        SHA256((unsigned char *)MESSAGE, strlen(MESSAGE), hash);

        // Firmar el mensaje
        start = get_time_in_ms();
        if (!RSA_sign(NID_sha256, hash, SHA256_DIGEST_LENGTH, signature, &sig_len, rsa)) {
            fprintf(stderr, "Error al firmar el mensaje: %s\n", ERR_error_string(ERR_get_error(), NULL));
            exit(EXIT_FAILURE);
        }
        end = get_time_in_ms();
        timings[i].sign = end - start;

        // Verificar la firma
        start = get_time_in_ms();
        if (!RSA_verify(NID_sha256, hash, SHA256_DIGEST_LENGTH, signature, sig_len, rsa)) {
            fprintf(stderr, "Error al verificar la firma: %s\n", ERR_error_string(ERR_get_error(), NULL));
            exit(EXIT_FAILURE);
        }
        end = get_time_in_ms();
        timings[i].verify = end - start;

        // Tiempo total
        timings[i].total = timings[i].gen_key + timings[i].sign + timings[i].verify;

        // Liberar recursos
        RSA_free(rsa);
        BN_free(e);
        free(signature);

        printf("Iteración %d completada: Gen Claves: %.3f ms, Firma: %.3f ms, Verificación: %.3f ms, Total: %.3f ms\n",
            i + 1, timings[i].gen_key, timings[i].sign, timings[i].verify, timings[i].total);
    }


    // Log resultados a un archivo CSV
    log_results_to_csv(filename, timings, n_iterations);

    // Calcular estadísticas
    double *gen_keys = malloc(n_iterations * sizeof(double));
    double *sign_keys = malloc(n_iterations * sizeof(double));
    double *verify_keys = malloc(n_iterations * sizeof(double));
    double *total_keys = malloc(n_iterations * sizeof(double));

    for (int i = 0; i < n_iterations; i++) {
        gen_keys[i] = timings[i].gen_key;
        sign_keys[i] = timings[i].sign;
        verify_keys[i] = timings[i].verify;
        total_keys[i] = timings[i].total;
    }

    double gen_avg = calculate_average(gen_keys, n_iterations);
    double sign_avg = calculate_average(sign_keys, n_iterations);
    double verify_avg = calculate_average(verify_keys, n_iterations);
    double total_avg = calculate_average(total_keys, n_iterations);

    double gen_std = calculate_stddev(gen_keys, n_iterations, gen_avg);
    double sign_std = calculate_stddev(sign_keys, n_iterations, sign_avg);
    double verify_std = calculate_stddev(verify_keys, n_iterations, verify_avg);
    double total_std = calculate_stddev(total_keys, n_iterations, total_avg);

    printf("\nResultados promedio para %d iteraciones:\n", n_iterations);
    printf("Tiempo de generación de claves: %.3f ms (+- %.3f)\n", gen_avg, gen_std);
    printf("Tiempo de creación de la firma: %.3f ms (+- %.3f)\n", sign_avg, sign_std);
    printf("Tiempo de verificación de la firma: %.3f ms (+- %.3f)\n", verify_avg, verify_std);
    printf("Tiempo total de ejecución: %.3f ms (+- %.3f)\n", total_avg, total_std);
    
    free(gen_keys);
    free(sign_keys);
    free(verify_keys);
    free(total_keys);
    free(timings);
}

// Implementaciones auxiliares
double calculate_average(double *data, int size) {
    double sum = 0.0;
    for (int i = 0; i < size; i++) {
        sum += data[i];
    }
    return sum / size;
}

double calculate_stddev(double *data, int size, double mean) {
    double sum = 0.0;
    for (int i = 0; i < size; i++) {
        sum += (data[i] - mean) * (data[i] - mean);
    }
    return sqrt(sum / (size - 1));
}

double get_time_in_ms() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

void log_results_to_csv(const char *filename, Timing *results, int n_iterations) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "Error al abrir el archivo CSV: %s\n", filename);
        exit(EXIT_FAILURE);
    }
    fprintf(file, "Iteración,Tiempo Generación Claves (ms),Tiempo Creación Firma (ms),Tiempo Verificación Firma (ms),Tiempo Total (ms)\n");
    for (int i = 0; i < n_iterations; i++) {
        fprintf(file, "%d,%.3f,%.3f,%.3f,%.3f\n",
                i + 1, results[i].gen_key, results[i].sign, results[i].verify, results[i].total);
    }
    fclose(file);
}

// Programa principal
int main() {
    int n_iterations = 100;

    // Ejecutar benchmarks para claves de 2048 y 4096 bits
    //run_rsa_benchmark(2048, n_iterations, "rsa_2048.csv");
    run_rsa_benchmark(4096, n_iterations, "rsa_4096.csv");

    return 0;
}
