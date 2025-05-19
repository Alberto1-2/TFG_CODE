package src;

import org.bouncycastle.crypto.AsymmetricCipherKeyPair;
import org.bouncycastle.pqc.crypto.crystals.dilithium.*;
import java.security.SecureRandom;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class Dilithium_RendGrafica {

    // Método para generar las claves
    private static AsymmetricCipherKeyPair generateKeyPair(DilithiumParameters params) {
        DilithiumKeyPairGenerator keyPairGenerator = new DilithiumKeyPairGenerator();
        DilithiumKeyGenerationParameters keyGenParams = new DilithiumKeyGenerationParameters(new SecureRandom(), params);
        keyPairGenerator.init(keyGenParams);
        return keyPairGenerator.generateKeyPair();
    }

    // Método para firmar un mensaje
    private static byte[] signMessage(byte[] message, DilithiumPrivateKeyParameters privateKey) {
        DilithiumSigner signer = new DilithiumSigner();
        signer.init(true, privateKey);
        return signer.generateSignature(message);
    }

    // Método para verificar la firma
    private static boolean verifySignature(byte[] message, byte[] signature, DilithiumPublicKeyParameters publicKey) {
        DilithiumSigner verifier = new DilithiumSigner();
        verifier.init(false, publicKey);
        return verifier.verifySignature(message, signature);
    }

    // Clase para almacenar estadísticas de rendimiento
    private static class Stats {
        List<Double> generationTimes = new ArrayList<>();
        List<Double> signingTimesSmall = new ArrayList<>();
        List<Double> signingTimesLarge = new ArrayList<>();
        List<Double> verificationTimesSmall = new ArrayList<>();
        List<Double> verificationTimesLarge = new ArrayList<>();

        double calculateAverage(List<Double> times) {
            return times.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        }

        double calculateStdDev(List<Double> times, double mean) {
            return Math.sqrt(times.stream().mapToDouble(t -> Math.pow(t - mean, 2)).average().orElse(0.0));
        }
    }

    // Clase para almacenar estadísticas globales
    private static class GlobalStats {
        String version;
        String messageSize;
        double avgKeyGen;
        double stdDevKeyGen;
        double avgSign;
        double stdDevSign;
        double avgVerify;
        double stdDevVerify;

        public GlobalStats(String version, String messageSize, Stats stats) {
            this.version = version;
            this.messageSize = messageSize;
            this.avgKeyGen = stats.calculateAverage(stats.generationTimes);
            this.stdDevKeyGen = stats.calculateStdDev(stats.generationTimes, avgKeyGen);
            this.avgSign = stats.calculateAverage(stats.signingTimesSmall);
            this.stdDevSign = stats.calculateStdDev(stats.signingTimesSmall, avgSign);
            this.avgVerify = stats.calculateAverage(stats.verificationTimesSmall);
            this.stdDevVerify = stats.calculateStdDev(stats.verificationTimesSmall, avgVerify);
        }

        public String toCsvLine() {
            DecimalFormat df = new DecimalFormat("0.0000");
            DecimalFormatSymbols dfs = new DecimalFormatSymbols(Locale.US);
            dfs.setDecimalSeparator('.');
            df.setDecimalFormatSymbols(dfs);

            return String.format("%s,%s,%s (+- %s),%s (+- %s),%s (+- %s)",
                    version, messageSize,
                    df.format(avgKeyGen), df.format(stdDevKeyGen),
                    df.format(avgSign), df.format(stdDevSign),
                    df.format(avgVerify), df.format(stdDevVerify));
        }
    }

    // Método principal
    public static void main(String[] args) {
        int iterations = 1000; // Número de iteraciones para las pruebas de rendimiento
        byte[] smallMessage = "Pruebas de Dilithium en java TFG".getBytes();
        byte[] largeMessage = new byte[10000]; // Mensaje de 10000 bytes
        new SecureRandom().nextBytes(largeMessage); // Rellena el mensaje grande con datos aleatorios

        // Versiones de Dilithium que vamos a probar
        DilithiumParameters[] versions = {
            DilithiumParameters.dilithium2,
            DilithiumParameters.dilithium3,
            DilithiumParameters.dilithium5
        };

        // Inicializar el archivo CSV para los resultados agregados (un único archivo para todas las versiones)
        try {
            saveAggregatedStatsToCsvHeader("Dilithium_Performance_Aggregated.csv");
        } catch (IOException e) {
            System.err.println("Error al crear el archivo CSV para los resultados agregados: " + e.getMessage());
            return;
        }

        // Realizar las pruebas para cada versión
        for (DilithiumParameters version : versions) {
            // Inicializar las estadísticas
            Stats stats = new Stats();
            List<Double> keyGenTimes = new ArrayList<>();
            List<Double> signTimesSmall = new ArrayList<>();
            List<Double> signTimesLarge = new ArrayList<>();
            List<Double> verifyTimesSmall = new ArrayList<>();
            List<Double> verifyTimesLarge = new ArrayList<>();

            // Variables para registrar el tiempo total de las iteraciones
            long totalStartTime = System.nanoTime();

            // Realizar las iteraciones
            for (int i = 0; i < iterations; i++) {
                // Generación de claves
                long start = System.nanoTime();
                AsymmetricCipherKeyPair keyPair = generateKeyPair(version);
                DilithiumPrivateKeyParameters privateKey = (DilithiumPrivateKeyParameters) keyPair.getPrivate();
                DilithiumPublicKeyParameters publicKey = (DilithiumPublicKeyParameters) keyPair.getPublic();
                long keyGenTime = System.nanoTime() - start;
                keyGenTimes.add(keyGenTime / 1_000_000.0); // en milisegundos

                // Firma de mensaje corto
                start = System.nanoTime();
                byte[] smallSignature = signMessage(smallMessage, privateKey);
                long signTimeSmall = System.nanoTime() - start;
                signTimesSmall.add(signTimeSmall / 1_000_000.0); // en milisegundos

                // Firma de mensaje grande
                start = System.nanoTime();
                byte[] largeSignature = signMessage(largeMessage, privateKey);
                long signTimeLarge = System.nanoTime() - start;
                signTimesLarge.add(signTimeLarge / 1_000_000.0); // en milisegundos

                // Verificación de firma en mensaje corto
                start = System.nanoTime();
                boolean isValidSmall = verifySignature(smallMessage, smallSignature, publicKey);
                long verifyTimeSmall = System.nanoTime() - start;
                verifyTimesSmall.add(verifyTimeSmall / 1_000_000.0); // en milisegundos

                // Verificación de firma en mensaje grande
                start = System.nanoTime();
                boolean isValidLarge = verifySignature(largeMessage, largeSignature, publicKey);
                long verifyTimeLarge = System.nanoTime() - start;
                verifyTimesLarge.add(verifyTimeLarge / 1_000_000.0); // en milisegundos

                // Validación de las firmas (opcional para pruebas)
                if (!isValidSmall || !isValidLarge) {
                    System.out.println("Error en la verificación de la firma en la iteración: " + i);
                }

                // Calcular el tiempo total pequeño (generación de claves + firma + verificación pequeña)
                double totalSmallTime = (keyGenTime + signTimeSmall + verifyTimeSmall) / 1_000_000.0; // en milisegundos

                // Calcular el tiempo total grande (generación de claves + firma + verificación grande)
                double totalLargeTime = (keyGenTime + signTimeLarge + verifyTimeLarge) / 1_000_000.0; // en milisegundos

                // Guardar los resultados de esta iteración en el archivo CSV para cada iteración
                try {
                    saveIterationToCsv(version, "Dilithium_Performance_Iteration.csv", i + 1, keyGenTime, signTimeSmall, signTimeLarge, verifyTimeSmall, verifyTimeLarge, totalSmallTime, totalLargeTime);
                } catch (IOException e) {
                    System.err.println("Error al guardar el archivo CSV para la iteración: " + e.getMessage());
                }
            }

            // Tiempo total de todas las iteraciones
            long totalEndTime = System.nanoTime();
            long totalElapsedTime = totalEndTime - totalStartTime;
            System.out.println("Tiempo total para " + version.getName() + ": " + totalElapsedTime / 1_000_000.0 + " ms");

            // Calcular estadísticas
            stats.generationTimes = keyGenTimes;
            stats.signingTimesSmall = signTimesSmall;
            stats.signingTimesLarge = signTimesLarge;
            stats.verificationTimesSmall = verifyTimesSmall;
            stats.verificationTimesLarge = verifyTimesLarge;

            // Crear objeto GlobalStats con los tiempos promedio y desviación estándar
            GlobalStats globalStats = new GlobalStats(version.getName(), "Pequeño", stats);

            // Guardar los resultados agregados (promedio y desviación estándar) en un único CSV
            try {
                saveAggregatedStatsToCsv("Dilithium_Performance_Aggregated.csv", globalStats);
            } catch (IOException e) {
                System.err.println("Error al guardar el archivo CSV con resultados agregados: " + e.getMessage());
            }

            stats.signingTimesSmall = signTimesLarge;
            stats.verificationTimesSmall = verifyTimesLarge;

            GlobalStats globalStatsLarge = new GlobalStats(version.getName(), "Grande", stats);
            try {
                saveAggregatedStatsToCsv("Dilithium_Performance_Aggregated.csv", globalStatsLarge);
            } catch (IOException e) {
                System.err.println("Error al guardar el archivo CSV con resultados agregados para el mensaje grande: " + e.getMessage());
            }
        }
    }

    private static void saveIterationToCsv(DilithiumParameters version, String fileName, int iteration, long keyGenTime, long signTimeSmall, long signTimeLarge, long verifyTimeSmall, long verifyTimeLarge, double totalSmallTime, double totalLargeTime) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(fileName, true))) {
            // Si es la primera iteración, agregar el encabezado del CSV
            if (iteration == 1) {
                writer.println("Iteración,Tiempo Generación Claves (ms),Tiempo Firma Pequeña (ms),Tiempo Firma Grande (ms),Tiempo Verificación Pequeña (ms),Tiempo Verificación Grande (ms),Tiempo Total Pequeño (ms),Tiempo Total Grande (ms)");
            }

            // Crear un DecimalFormat para asegurarnos de usar el punto como separador decimal
            DecimalFormat df = new DecimalFormat("0.0000");
            DecimalFormatSymbols dfs = new DecimalFormatSymbols(Locale.US);
            dfs.setDecimalSeparator('.');
            df.setDecimalFormatSymbols(dfs);

            // Escribir los resultados de la iteración utilizando df.format() para formatear los tiempos
            writer.printf("%d,%s,%s,%s,%s,%s,%s,%s%n", iteration,
                df.format(keyGenTime / 1_000_000.0),  // Convertir y formatear con 4 decimales
                df.format(signTimeSmall / 1_000_000.0),
                df.format(signTimeLarge / 1_000_000.0),
                df.format(verifyTimeSmall / 1_000_000.0),
                df.format(verifyTimeLarge / 1_000_000.0),
                df.format(totalSmallTime),
                df.format(totalLargeTime)
            );
        }
    }

    // Guardar el encabezado en el archivo CSV de resultados agregados
    private static void saveAggregatedStatsToCsvHeader(String fileName) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(fileName, true))) {
            writer.println("Versión,Tamaño Mensaje,Tiempo Generación Claves (±Desviación),Tiempo Firma (±Desviación),Tiempo Verificación (±Desviación)");
        }
    }

    // Guardar los resultados agregados (promedio y desviación estándar) en un archivo CSV
    private static void saveAggregatedStatsToCsv(String fileName, GlobalStats stats) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(fileName, true))) {
            writer.println(stats.toCsvLine());
        }
        System.out.println("Resultados agregados guardados en " + fileName);
    }
}
