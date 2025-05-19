package src;

import java.io.FileWriter;
import java.io.PrintWriter;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.List;
import org.bouncycastle.crypto.AsymmetricCipherKeyPair;
import org.bouncycastle.crypto.params.ParametersWithRandom;
import org.bouncycastle.pqc.crypto.sphincsplus.*;

// Para pasar de , a . en los valores para csv
import java.util.Locale; // Import necesario


public class SphincsPlusRendimientoGrafica {

    public void pruebaRendimiento(int messageSize, int iterations, SPHINCSPlusParameters tipo, String iterFileName, String resumenFileName) throws Exception {
        byte[] msg = new byte[messageSize];
        SecureRandom random = new SecureRandom();
        random.nextBytes(msg);

        SPHINCSPlusKeyPairGenerator keyGen = new SPHINCSPlusKeyPairGenerator();
        keyGen.init(new SPHINCSPlusKeyGenerationParameters(random, tipo));

        List<Double> genKeyTimes = new ArrayList<>();
        List<Double> signTimes = new ArrayList<>();
        List<Double> verifyTimes = new ArrayList<>();

        try (PrintWriter iterWriter = new PrintWriter(new FileWriter(iterFileName, true))) {
            iterWriter.println("Iteración,Tipo,Tiempo Generación Claves,Tiempo Firma,Tiempo Verificación,Tiempo Total");

            for (int i = 0; i < iterations; i++) {
                double startTime, endTime, genKeyTime, signTime, verifyTime, totalTime;

                // Generar claves
                startTime = System.nanoTime();
                AsymmetricCipherKeyPair keyPair = keyGen.generateKeyPair();
                endTime = System.nanoTime();
                genKeyTime = (endTime - startTime) / 1_000_000.0;
                genKeyTimes.add(genKeyTime);

                SPHINCSPlusPrivateKeyParameters skParam = (SPHINCSPlusPrivateKeyParameters) keyPair.getPrivate();
                SPHINCSPlusPublicKeyParameters pkParam = (SPHINCSPlusPublicKeyParameters) keyPair.getPublic();

                // Firmar mensaje
                SPHINCSPlusSigner signer = new SPHINCSPlusSigner();
                signer.init(true, new ParametersWithRandom(skParam, random));

                startTime = System.nanoTime();
                byte[] sigGenerated = signer.generateSignature(msg);
                endTime = System.nanoTime();
                signTime = (endTime - startTime) / 1_000_000.0;
                signTimes.add(signTime);

                // Verificar firma
                SPHINCSPlusSigner verifier = new SPHINCSPlusSigner();
                verifier.init(false, pkParam);

                startTime = System.nanoTime();
                boolean isVerified = verifier.verifySignature(msg, sigGenerated);
                endTime = System.nanoTime();
                verifyTime = (endTime - startTime) / 1_000_000.0;
                verifyTimes.add(verifyTime);

                if (!isVerified) {
                    System.err.println("Falló la verificación en la iteración " + (i + 1));
                }

                // Calcular tiempo total
                totalTime = genKeyTime + signTime + verifyTime;

                // Escribir resultado por iteración
                String tipoDescripcion = SphincsPlusRendimientoGrafica.getHashDescription(tipo);
                //iterWriter.printf("%d,%s,%d,%.3f,%.3f,%.3f,%.3f%n", i + 1, tipoDescripcion, messageSize, genKeyTime, signTime, verifyTime, totalTime);
                iterWriter.printf(Locale.US, "%d,\"%s\",%.3f,%.3f,%.3f,%.3f%n", i + 1, tipoDescripcion, genKeyTime, signTime, verifyTime, totalTime);

                

            }
        }

        // Calcular promedios y desviaciones
        double avgGenKey = calculateAverage(genKeyTimes);
        double stdDevGenKey = calculateStdDev(genKeyTimes, avgGenKey);

        double avgSign = calculateAverage(signTimes);
        double stdDevSign = calculateStdDev(signTimes, avgSign);

        double avgVerify = calculateAverage(verifyTimes);
        double stdDevVerify = calculateStdDev(verifyTimes, avgVerify);

        // Escribir resumen global
        try (PrintWriter resumenWriter = new PrintWriter(new FileWriter(resumenFileName, true))) {
            String tipoDescripcion = SphincsPlusRendimientoGrafica.getHashDescription(tipo);
            //resumenWriter.printf("%s,%d,%.4f (+- %.4f),%.4f (+- %.4f),%.4f (+- %.4f)%n",
            resumenWriter.printf(Locale.US, "%s\",%.4f (+- %.4f),%.4f (+- %.4f),%.4f (+- %.4f)%n",

                    tipoDescripcion,
                    avgGenKey, stdDevGenKey,
                    avgSign, stdDevSign,
                    avgVerify, stdDevVerify);
        }
    }

    public static double calculateAverage(List<Double> values) {
        return values.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
    }

    public static double calculateStdDev(List<Double> values, double mean) {
        return Math.sqrt(values.stream().mapToDouble(v -> Math.pow(v - mean, 2)).average().orElse(0.0));
    }

    public static void main(String[] args) {
        SphincsPlusRendimientoGrafica prueba = new SphincsPlusRendimientoGrafica();
        int[] messageSizes = {10000};
        SPHINCSPlusParameters[] tipos = {
            SPHINCSPlusParameters.sha2_128f_robust, SPHINCSPlusParameters.sha2_192f_robust,
            SPHINCSPlusParameters.sha2_256f_robust, SPHINCSPlusParameters.sha2_128s_robust,
            SPHINCSPlusParameters.sha2_192s_robust, SPHINCSPlusParameters.sha2_256s_robust,
            SPHINCSPlusParameters.shake_128f_robust, SPHINCSPlusParameters.shake_192f_robust,
            SPHINCSPlusParameters.shake_256f_robust, SPHINCSPlusParameters.shake_128s_robust,
            SPHINCSPlusParameters.shake_192s_robust, SPHINCSPlusParameters.shake_256s_robust
        };

        for (int messageSize : messageSizes) {
            for (SPHINCSPlusParameters spp : tipos) {
                String tipoDescripcion = SphincsPlusRendimientoGrafica.getHashDescription(spp);
                String iterFileName = "sphincsplus_iter_" + tipoDescripcion.replace(" ", "_") + "_" + messageSize + "bytes.csv";
                String resumenFileName = "sphincsplus_resumen.csv";

                System.out.println("\n--- Prueba con mensaje de tamaño " + messageSize + " bytes ---");
                System.out.println("Configuración: " + tipoDescripcion);

                try {
                    prueba.pruebaRendimiento(messageSize, 100, spp, iterFileName, resumenFileName);
                } catch (Exception e) {
                    System.err.println("Error durante la prueba: " + e.getMessage());
                    e.printStackTrace();
                }
            }
        }
    }

    public static String getHashDescription(SPHINCSPlusParameters spp) {
        if (spp == SPHINCSPlusParameters.sha2_128f_robust) return "SHA-2_128-bit, robust";
        if (spp == SPHINCSPlusParameters.sha2_192f_robust) return "SHA-2_192-bit, robust";
        if (spp == SPHINCSPlusParameters.sha2_256f_robust) return "SHA-2_256-bit, robust";
        if (spp == SPHINCSPlusParameters.sha2_128s_robust) return "SHA-2_128-bit, standard_robust";
        if (spp == SPHINCSPlusParameters.sha2_192s_robust) return "SHA-2_192-bit, standard_robust";
        if (spp == SPHINCSPlusParameters.sha2_256s_robust) return "SHA-2_256-bit, standard_robust";
        if (spp == SPHINCSPlusParameters.shake_128f_robust) return "SHAKE-128, robust";
        if (spp == SPHINCSPlusParameters.shake_192f_robust) return "SHAKE-192, robust";
        if (spp == SPHINCSPlusParameters.shake_256f_robust) return "SHAKE-256, robust";
        if (spp == SPHINCSPlusParameters.shake_128s_robust) return "SHAKE-128, standard_robust";
        if (spp == SPHINCSPlusParameters.shake_192s_robust) return "SHAKE-192, standard_robust";
        if (spp == SPHINCSPlusParameters.shake_256s_robust) return "SHAKE-256, standard_robust";
        return "Desconocido";
    }
    
    
}
