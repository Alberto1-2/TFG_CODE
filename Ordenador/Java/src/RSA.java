package src;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import java.util.Locale;

public class RSA {

    // Configuración global del separador decimal y Locale
    static {
        Locale.setDefault(Locale.US);
    }
    public static void main(String[] args) {
        // Registrar Bouncy Castle como proveedor
        Security.addProvider(new BouncyCastleProvider());

        // Parámetros para las pruebas
        int nIterations = 1000;

        // Medir el rendimiento para claves de 2048 y 4096 bits
        medirRendimiento(2048, nIterations, "rsa_2048.csv");
        medirRendimiento(4096, nIterations, "rsa_4096.csv");
    }

    // Función para medir el rendimiento de generación de claves, firma y verificación
    public static void medirRendimiento(int bits, int nIterations, String filename) {
        System.out.printf("\nIniciando pruebas para claves RSA de %d bits...\n", bits);

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            writer.write("Iteración,Tiempo Generación Claves (ms),Tiempo Creación Firma (ms),Tiempo Verificación Firma (ms),Tiempo Total (ms)\n");

            List<Double> tiemposGeneracion = new ArrayList<>();
            List<Double> tiemposFirma = new ArrayList<>();
            List<Double> tiemposVerificacion = new ArrayList<>();
            List<Double> tiemposTotales = new ArrayList<>();

            for (int i = 1; i <= nIterations; i++) {
                try {
                    // Medir generación de claves
                    long start = System.nanoTime();
                    KeyPairGenerator keyPairGen = KeyPairGenerator.getInstance("RSA", "BC");
                    keyPairGen.initialize(bits);
                    KeyPair keyPair = keyPairGen.generateKeyPair();
                    long end = System.nanoTime();
                    double tiempoGeneracion = (end - start) / 1_000_000.0;
                    tiemposGeneracion.add(tiempoGeneracion);

                    // Crear un mensaje de prueba
                    byte[] mensaje = "Este es un mensaje de prueba para firmar.".getBytes(StandardCharsets.UTF_8);

                    // Medir creación de firma
                    start = System.nanoTime();
                    Signature firma = Signature.getInstance("SHA256withRSA", "BC");
                    firma.initSign(keyPair.getPrivate());
                    firma.update(mensaje);
                    byte[] firmaBytes = firma.sign();
                    end = System.nanoTime();
                    double tiempoFirma = (end - start) / 1_000_000.0;
                    tiemposFirma.add(tiempoFirma);

                    // Medir verificación de la firma
                    start = System.nanoTime();
                    Signature verificacion = Signature.getInstance("SHA256withRSA", "BC");
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
