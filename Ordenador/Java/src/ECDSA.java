package src;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.spec.ECGenParameterSpec;
import java.util.*;
import org.bouncycastle.jce.provider.BouncyCastleProvider;

public class ECDSA {

    // Configuración global del separador decimal y Locale
    static {
        Locale.setDefault(Locale.US);
    }
    public static void main(String[] args) {
        // Registrar Bouncy Castle como proveedor
        Security.addProvider(new BouncyCastleProvider());

        // Parámetros para las pruebas
        int nIterations = 1000;

        // Medir el rendimiento para curvas secp256r1 y secp384r1
        medirRendimiento("secp256r1", nIterations, "ecdsa_secp256r1.csv");
        medirRendimiento("secp384r1", nIterations, "ecdsa_secp384r1.csv");
    }

    // Función para medir el rendimiento de generación de claves, firma y verificación
    public static void medirRendimiento(String curveName, int nIterations, String filename) {
        System.out.printf("\nIniciando pruebas para la curva %s...\n", curveName);
       

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            writer.write("Iteración,Tiempo Generación Claves (ms),Tiempo Creación Firma (ms),Tiempo Verificación Firma (ms),Tiempo Total (ms)\n");

            List<Double> tiemposGeneracion = new ArrayList<>();
            List<Double> tiemposFirma = new ArrayList<>();
            List<Double> tiemposVerificacion = new ArrayList<>();
            List<Double> tiemposTotales = new ArrayList<>();
            
            // HACEMOS prueba de warmup (calentamiento para evitar distorsionar los resultados de las gráficas)
            try {
                // Creación de las claves 
                KeyPairGenerator keyPairGen_warmup = KeyPairGenerator.getInstance("EC", "BC");
                keyPairGen_warmup.initialize(new ECGenParameterSpec(curveName));
                KeyPair keyPair_warmup = keyPairGen_warmup.generateKeyPair();

                // Creamos un mensaje de prueba
                byte[] mensaje_warmup = "Este es un mensaje de prueba para firmar.".getBytes(StandardCharsets.UTF_8);

                // Creamos la firma
                Signature firma_warmup = Signature.getInstance("SHA256withECDSA", "BC");
                firma_warmup.initSign(keyPair_warmup.getPrivate());
                firma_warmup.update(mensaje_warmup);
                byte[] firmaBytes_wup = firma_warmup.sign();

                // Verificamos la firma
                Signature verificacion = Signature.getInstance("SHA256withECDSA", "BC");
                verificacion.initVerify(keyPair_warmup.getPublic());
                verificacion.update(mensaje_warmup);
                boolean esValida = verificacion.verify(firmaBytes_wup);

                if (!esValida) {
                    System.out.printf("Error, firma no válida\n");
                }

                
            } catch (Exception e) {
                System.err.printf("Error %s\n", e.getMessage());
            }

            for (int i = 1; i <= nIterations; i++) {
                try {
                    // Medir generación de claves
                    long start = System.nanoTime();
                    KeyPairGenerator keyPairGen = KeyPairGenerator.getInstance("EC", "BC");
                    keyPairGen.initialize(new ECGenParameterSpec(curveName));
                    KeyPair keyPair = keyPairGen.generateKeyPair();
                    long end = System.nanoTime();
                    double tiempoGeneracion = (end - start) / 1_000_000.0;
                    tiemposGeneracion.add(tiempoGeneracion);

                    // Crear un mensaje de prueba
                    byte[] mensaje = "Este es un mensaje de prueba para firmar.".getBytes(StandardCharsets.UTF_8);

                    // Medir creación de firma
                    start = System.nanoTime();
                    Signature firma = Signature.getInstance("SHA256withECDSA", "BC");
                    firma.initSign(keyPair.getPrivate());
                    firma.update(mensaje);
                    byte[] firmaBytes = firma.sign();
                    end = System.nanoTime();
                    double tiempoFirma = (end - start) / 1_000_000.0;
                    tiemposFirma.add(tiempoFirma);

                    // Medir verificación de la firma
                    start = System.nanoTime();
                    Signature verificacion = Signature.getInstance("SHA256withECDSA", "BC");
                    verificacion.initVerify(keyPair.getPublic());
                    verificacion.update(mensaje);
                    boolean esValida = verificacion.verify(firmaBytes);
                    end = System.nanoTime();
                    double tiempoVerificacion = (end - start) / 1_000_000.0;
                    tiemposVerificacion.add(tiempoVerificacion);

                    if (!esValida) {
                        System.out.printf("Advertencia: Firma no válida en la iteración %d\n", i);
                    }

                    // Calcular tiempo total
                    double tiempoTotal = tiempoGeneracion + tiempoFirma + tiempoVerificacion;
                    tiemposTotales.add(tiempoTotal);

                    // Escribir resultados en el archivo CSV
                    writer.write(String.format(Locale.US, "%d,%.3f,%.3f,%.3f,%.3f\n", i, tiempoGeneracion, tiempoFirma, tiempoVerificacion, tiempoTotal));
                    System.out.printf("Iteración %d completada.\n", i);
                } catch (Exception e) {
                    System.err.printf("Error en la iteración %d: %s\n", i, e.getMessage());
                }
            }

            // Mostrar resultados promedio y desviación estándar
            mostrarResultados(tiemposGeneracion, "Generación de claves");
            mostrarResultados(tiemposFirma, "Creación de firmas");
            mostrarResultados(tiemposVerificacion, "Verificación de firmas");
            mostrarResultados(tiemposTotales, "Tiempo total");
        } catch (IOException e) {
            System.err.println("Error al escribir el archivo CSV: " + e.getMessage());
        }
    }

    // Función para calcular promedio
    private static double calcularPromedio(List<Double> valores) {
        return valores.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
    }

    // Función para calcular desviación estándar
    private static double calcularDesviacionEstandar(List<Double> valores) {
        double promedio = calcularPromedio(valores);
        return Math.sqrt(valores.stream().mapToDouble(v -> Math.pow(v - promedio, 2)).sum() / (valores.size() - 1));
    }

    // Función para mostrar resultados promedio y desviación estándar
    private static void mostrarResultados(List<Double> tiempos, String tipo) {
        double promedio = calcularPromedio(tiempos);
        double desviacion = calcularDesviacionEstandar(tiempos);
        System.out.printf("%s: Promedio = %.3f ms, Desviación estándar = %.3f ms\n", tipo, promedio, desviacion);
    }
}
