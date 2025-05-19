package src;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.security.SecureRandom;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import org.bouncycastle.crypto.AsymmetricCipherKeyPair;
import org.bouncycastle.crypto.params.ParametersWithRandom;
import org.bouncycastle.pqc.crypto.falcon.FalconKeyGenerationParameters;
import org.bouncycastle.pqc.crypto.falcon.FalconKeyPairGenerator;
import org.bouncycastle.pqc.crypto.falcon.FalconParameters;
import org.bouncycastle.pqc.crypto.falcon.FalconPrivateKeyParameters;
import org.bouncycastle.pqc.crypto.falcon.FalconPublicKeyParameters;
import org.bouncycastle.pqc.crypto.falcon.FalconSigner;

public class FalconJavaBenchmark {

    // Configuración global del separador decimal y Locale
    static {
        Locale.setDefault(Locale.US);
    }

    private static class Stats {
        List<Double> generationTimes = new ArrayList<>();
        List<Double> signingTimes = new ArrayList<>();
        List<Double> verificationTimes = new ArrayList<>();

        double calculateAverage(List<Double> times) {
            return times.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        }

        double calculateStdDev(List<Double> times, double mean) {
            return Math.sqrt(times.stream().mapToDouble(t -> Math.pow(t - mean, 2)).average().orElse(0.0));
        }
    }

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
            this.avgSign = stats.calculateAverage(stats.signingTimes);
            this.stdDevSign = stats.calculateStdDev(stats.signingTimes, avgSign);
            this.avgVerify = stats.calculateAverage(stats.verificationTimes);
            this.stdDevVerify = stats.calculateStdDev(stats.verificationTimes, avgVerify);
        }

        public String toCsvLine() {
            // Crear el formato deseado con 4 decimales y el formato "(+-)"
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

    public void benchmarkFalcon(FalconParameters falconParams, int messageSize, String testLabel, int iterations, Stats globalStats, List<GlobalStats> globalStatsList) throws Exception {
        byte[] msg = new byte[messageSize];
        new SecureRandom().nextBytes(msg); // Generar mensaje aleatorio

        SecureRandom random = new SecureRandom();
        FalconKeyPairGenerator keyGen = new FalconKeyPairGenerator();
        keyGen.init(new FalconKeyGenerationParameters(random, falconParams));

        Stats stats = new Stats();
        boolean verificationFailed = false;

        // Pruebas
        for (int i = 0; i < iterations; i++) {
            // Generación de claves
            long startTime = System.nanoTime();
            AsymmetricCipherKeyPair keyPair = keyGen.generateKeyPair();
            long endTime = System.nanoTime();
            stats.generationTimes.add((endTime - startTime) / 1_000_000.0); // ms

            // Firma
            FalconSigner signer = new FalconSigner();
            FalconPrivateKeyParameters skParam = (FalconPrivateKeyParameters) keyPair.getPrivate();
            ParametersWithRandom skwrand = new ParametersWithRandom(skParam, random);
            signer.init(true, skwrand);

            startTime = System.nanoTime();
            byte[] signature = signer.generateSignature(msg);
            endTime = System.nanoTime();
            stats.signingTimes.add((endTime - startTime) / 1_000_000.0); // ms

            // Verificación
            FalconSigner verifier = new FalconSigner();
            FalconPublicKeyParameters pkParam = (FalconPublicKeyParameters) keyPair.getPublic();
            verifier.init(false, pkParam);

            startTime = System.nanoTime();
            boolean isVerified = verifier.verifySignature(msg, signature);
            endTime = System.nanoTime();
            stats.verificationTimes.add((endTime - startTime) / 1_000_000.0); // ms

            if (!isVerified) {
                System.err.println("Error: La verificación falló en la iteración " + i);
                verificationFailed = true;
            }
        }

        if (!verificationFailed) {
            System.out.println("Todas las firmas verificadas correctamente.");
        }

        // Guardar resultados en CSV
        String fileName = String.format("%s_%s_performance.csv", falconParams.getName(), testLabel);
        saveToCsv(fileName, stats, iterations, falconParams.getName(), testLabel);

        // Agregar estadísticas locales a las globales
        globalStats.generationTimes.addAll(stats.generationTimes);
        globalStats.signingTimes.addAll(stats.signingTimes);
        globalStats.verificationTimes.addAll(stats.verificationTimes);

        // Guardar estadísticas globales con el tamaño de mensaje
        GlobalStats globalStatsWithSize = new GlobalStats(falconParams.getName(), testLabel, stats);
        globalStatsList.add(globalStatsWithSize);
    }

    private void saveToCsv(String fileName, Stats stats, int iterations, String version, String label) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(fileName))) {
            writer.println("Iteración,Falcon Version,Tamaño Mensaje,Tiempo Generación Claves,Tiempo Firma,Tiempo Verificación,Tiempo Total");
            for (int i = 0; i < iterations; i++) {
                double keyGenTime = stats.generationTimes.get(i);
                double signTime = stats.signingTimes.get(i);
                double verifyTime = stats.verificationTimes.get(i);
                double totalTime = keyGenTime + signTime + verifyTime;
                writer.printf("%d,%s,%s,%.4f,%.4f,%.4f,%.4f%n", i + 1, version, label, keyGenTime, signTime, verifyTime, totalTime);
            }
        }
        System.out.println("Resultados guardados en " + fileName);
    }

    private void saveGlobalStatsToCsv(String fileName, List<GlobalStats> globalStatsList) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(fileName))) {
            writer.println("Versión,Tamaño Mensaje,Tiempo Generación Claves (±Desviación),Tiempo Firma (±Desviación),Tiempo Verificación (±Desviación)");
            for (GlobalStats stats : globalStatsList) {
                writer.println(stats.toCsvLine());
            }
        }
        System.out.println("Resultados globales guardados en " + fileName);
    }

    public static void main(String[] args) {
        FalconJavaBenchmark benchmark = new FalconJavaBenchmark();

        // Parámetros de prueba
        int[] messageSizes = {32, 10000}; // Pequeño y grande
        int iterations = 1000; // Número de repeticiones

        List<GlobalStats> globalStatsList = new ArrayList<>();

        try {
            for (FalconParameters falconParams : new FalconParameters[]{FalconParameters.falcon_512, FalconParameters.falcon_1024}) {
                Stats globalStats = new Stats();

                for (int messageSize : messageSizes) {
                    String label = (messageSize == 32 ? "pequeño" : "grande");
                    System.out.printf("\n--- Prueba con %s, mensaje %s (%d bytes) ---\n", falconParams.getName(), label, messageSize);
                    benchmark.benchmarkFalcon(falconParams, messageSize, label, iterations, globalStats, globalStatsList);
                }
            }

            // Guardar estadísticas globales
            benchmark.saveGlobalStatsToCsv("Falcon_Global_Stats.csv", globalStatsList);

        } catch (Exception e) {
            System.err.println("Error durante la prueba de rendimiento: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
