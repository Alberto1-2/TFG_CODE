package src;

import org.bouncycastle.jcajce.SecretKeyWithEncapsulation;
import org.bouncycastle.jcajce.spec.KEMExtractSpec;
import org.bouncycastle.jcajce.spec.KEMGenerateSpec;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.pqc.jcajce.provider.BouncyCastlePQCProvider;
import org.bouncycastle.pqc.jcajce.spec.KyberParameterSpec;

import java.security.*;
import java.security.spec.AlgorithmParameterSpec;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.spec.SecretKeySpec;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class Kyber_RendGrafica {

    private static final String KEM_ALGORITHM = "Kyber";
    private static final String PROVIDER = "BCPQC";
    private static final String ENCRYPTION_ALGORITHM = "AES";
    private static final String MODE_PADDING = "AES/ECB/PKCS5Padding";
    private static final int NUM_TESTS = 1000;

    // Método para cifrar
    public static String encrypt(String plainText, byte[] key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key, ENCRYPTION_ALGORITHM);
        Cipher cipher = Cipher.getInstance(MODE_PADDING);
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes());
        return java.util.Base64.getEncoder().encodeToString(encryptedBytes);
    }

    // Método para descifrar
    public static String decrypt(String encryptedText, byte[] key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key, ENCRYPTION_ALGORITHM);
        Cipher cipher = Cipher.getInstance(MODE_PADDING);
        cipher.init(Cipher.DECRYPT_MODE, secretKey);
        byte[] decodedBytes = java.util.Base64.getDecoder().decode(encryptedText);
        byte[] decryptedBytes = cipher.doFinal(decodedBytes);
        return new String(decryptedBytes);
    }

    // Método para generar el par de claves Kyber
    private static KeyPair generateKeyPair(AlgorithmParameterSpec parameterSpec) throws NoSuchAlgorithmException, NoSuchProviderException, InvalidAlgorithmParameterException {
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(KEM_ALGORITHM, PROVIDER);
        keyPairGenerator.initialize(parameterSpec, new SecureRandom());
        return keyPairGenerator.generateKeyPair();
    }

    // Método para generar clave secreta para el remitente
    private static SecretKeyWithEncapsulation generateSecretKeySender(PublicKey publicKey, AlgorithmParameterSpec parameterSpec) throws NoSuchAlgorithmException, NoSuchProviderException, InvalidAlgorithmParameterException {
        KeyGenerator keyGenerator = KeyGenerator.getInstance(KEM_ALGORITHM, PROVIDER);
        KEMGenerateSpec kemGenerateSpec = new KEMGenerateSpec(publicKey, "Secret");
        keyGenerator.init(kemGenerateSpec);
        return (SecretKeyWithEncapsulation) keyGenerator.generateKey();
    }

    // Método para generar clave secreta para el receptor
    private static SecretKeyWithEncapsulation generateSecretKeyReceiver(PrivateKey privateKey, byte[] encapsulation) throws NoSuchAlgorithmException, NoSuchProviderException, InvalidAlgorithmParameterException {
        KEMExtractSpec kemExtractSpec = new KEMExtractSpec(privateKey, encapsulation, "Secret");
        KeyGenerator keyGenerator = KeyGenerator.getInstance(KEM_ALGORITHM, PROVIDER);
        keyGenerator.init(kemExtractSpec);
        return (SecretKeyWithEncapsulation) keyGenerator.generateKey();
    }

    // Método para guardar los resultados agregados en un archivo CSV
    private static void saveAggregatedStatsToCsv(String fileName, String version, List<Double> keyGenTimes, List<Double> encapTimes, List<Double> decapTimes, List<Double> encryptTimes, List<Double> decryptTimes) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(fileName, true))) {
            DecimalFormat df = new DecimalFormat("0.00000000"); // Asegurarse de tener suficiente precisión
            DecimalFormatSymbols dfs = new DecimalFormatSymbols(Locale.US);
            dfs.setDecimalSeparator('.');
            df.setDecimalFormatSymbols(dfs);

            double avgKeyGen = keyGenTimes.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double avgEncap = encapTimes.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double avgDecap = decapTimes.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double avgEncrypt = encryptTimes.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double avgDecrypt = decryptTimes.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);

            double stdDevKeyGen = Math.sqrt(keyGenTimes.stream().mapToDouble(t -> Math.pow(t - avgKeyGen, 2)).average().orElse(0.0));
            double stdDevEncap = Math.sqrt(encapTimes.stream().mapToDouble(t -> Math.pow(t - avgEncap, 2)).average().orElse(0.0));
            double stdDevDecap = Math.sqrt(decapTimes.stream().mapToDouble(t -> Math.pow(t - avgDecap, 2)).average().orElse(0.0));
            double stdDevEncrypt = Math.sqrt(encryptTimes.stream().mapToDouble(t -> Math.pow(t - avgEncrypt, 2)).average().orElse(0.0));
            double stdDevDecrypt = Math.sqrt(decryptTimes.stream().mapToDouble(t -> Math.pow(t - avgDecrypt, 2)).average().orElse(0.0));

            writer.printf("%s,%s,%s (+- %s),%s (+- %s),%s (+- %s),%s (+- %s),%s (+- %s)%n",
                    version, "Kyber",
                    df.format(avgKeyGen), df.format(stdDevKeyGen),
                    df.format(avgEncap), df.format(stdDevEncap),
                    df.format(avgDecap), df.format(stdDevDecap),
                    df.format(avgEncrypt), df.format(stdDevEncrypt),
                    df.format(avgDecrypt), df.format(stdDevDecrypt));
        }
    }

    private static void saveIterationStatsToCsv(String fileName, String version, int iteration, double keyGenTime, double encapTime, double decapTime, double encryptTime, double decryptTime) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(fileName, true))) {
            DecimalFormat df = new DecimalFormat("0.0000"); // Formato con 4 decimales
            DecimalFormatSymbols dfs = new DecimalFormatSymbols(Locale.US);
            dfs.setDecimalSeparator('.');
            df.setDecimalFormatSymbols(dfs);  // Asegurarse de usar punto como separador decimal
    
            // Calculamos el tiempo total de la iteración
            double totalTime = keyGenTime + encapTime + decapTime + encryptTime + decryptTime;
    
            // Guardamos los resultados en el archivo CSV
            writer.printf("%s,%d,%s,%s,%s,%s,%s,%s%n", version, iteration, 
                          df.format(keyGenTime), df.format(encapTime), 
                          df.format(decapTime), df.format(encryptTime), 
                          df.format(decryptTime), df.format(totalTime));
        }
    }

    public static void main(String[] args) throws Exception {
        // Añadir los proveedores necesarios
        Security.addProvider(new BouncyCastleProvider());
        Security.addProvider(new BouncyCastlePQCProvider());
    
        // Las 3 versiones de Kyber que vamos a probar
        KyberParameterSpec[] kyberSpecs = {
            KyberParameterSpec.kyber512,
            KyberParameterSpec.kyber768,
            KyberParameterSpec.kyber1024
        };
    
        // Guardar los resultados de iteración en un CSV
        String iterationResultsCsv = "Kyber_Iteration_Results.csv";
        try (PrintWriter writer = new PrintWriter(new FileWriter(iterationResultsCsv))) {
            writer.println("Version,Iteration,KeyGenTime,EncapTime,DecapTime,EncryptTime,DecryptTime,TotalTime");
        }
    
        // Realizar las pruebas para cada versión de Kyber
        for (KyberParameterSpec kyberSpec : kyberSpecs) {
            List<Double> keyGenTimes = new ArrayList<>();
            List<Double> encapTimes = new ArrayList<>();
            List<Double> decapTimes = new ArrayList<>();
            List<Double> encryptTimes = new ArrayList<>();
            List<Double> decryptTimes = new ArrayList<>();
    
            // Realizar las pruebas NUM_TESTS veces
            for (int i = 0; i < NUM_TESTS; i++) {
                long startTime, endTime;
    
                // Medir el tiempo de generación de la clave
                startTime = System.nanoTime();
                KeyPair keyPair = generateKeyPair(kyberSpec);
                endTime = System.nanoTime();
                double keyGenTime = (endTime - startTime) / 1000000.0; // Tiempo en milisegundos
    
                // Medir el tiempo de encapsulación
                startTime = System.nanoTime();
                SecretKeyWithEncapsulation keyWithEnc = generateSecretKeySender(keyPair.getPublic(), kyberSpec);
                endTime = System.nanoTime();
                double encapTime = (endTime - startTime) / 1000000.0;  // Convertir a milisegundos
    
                // Medir el tiempo de descapsulación
                startTime = System.nanoTime();
                SecretKeyWithEncapsulation receivedKey = generateSecretKeyReceiver(keyPair.getPrivate(), keyWithEnc.getEncapsulation());
                endTime = System.nanoTime();
                double decapTime = (endTime - startTime) / 1000000.0;  // Convertir a milisegundos
    
                // Medir el tiempo de cifrado
                startTime = System.nanoTime();
                String encryptedMessage = encrypt("Hello, Kyber!", receivedKey.getEncoded());
                endTime = System.nanoTime();
                double encryptTime = (endTime - startTime) / 1000000.0; // Tiempo en milisegundos
    
                // Medir el tiempo de descifrado
                startTime = System.nanoTime();
                String decryptedMessage = decrypt(encryptedMessage, receivedKey.getEncoded());
                endTime = System.nanoTime();
                double decryptTime = (endTime - startTime) / 1000000.0; // Tiempo en milisegundos
    
                // Guardar los resultados de la iteración en un archivo CSV
                saveIterationStatsToCsv(iterationResultsCsv, kyberSpec.getName(), i + 1, keyGenTime, encapTime, decapTime, encryptTime, decryptTime);
    
                // Acumular los tiempos para estadísticas agregadas
                keyGenTimes.add(keyGenTime);
                encapTimes.add(encapTime);
                decapTimes.add(decapTime);
                encryptTimes.add(encryptTime);
                decryptTimes.add(decryptTime);
            }
    
            // Guardar estadísticas agregadas en un archivo CSV
            String aggregatedStatsCsv = "Kyber_Aggregated_Stats.csv";
            saveAggregatedStatsToCsv(aggregatedStatsCsv, kyberSpec.getName(), keyGenTimes, encapTimes, decapTimes, encryptTimes, decryptTimes);
        }
    }
}
