using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;

class RSAExample
{
    static void Main(string[] args)
    {
        // Parámetros para las pruebas
        int nIterations = 1000;

        // Medir el rendimiento para claves de 2048 y 4096 bits
        //MedirRendimiento(2048, nIterations, "rsa1_2048.csv");
        MedirRendimiento(4096, nIterations, "rsa1_4096.csv");
    }

    // Función para medir el rendimiento de la generación de claves, creación y verificación de firmas
    static void MedirRendimiento(int bits, int nIterations, string filename)
    {
        // Configuración cultural para separar decimales con "."
        CultureInfo.DefaultThreadCurrentCulture = new CultureInfo("en-US");
        Console.WriteLine($"\nIniciando pruebas para claves RSA de {bits} bits...");

        // Crear el archivo CSV
        using (var writer = new StreamWriter(filename))
        using (SHA256 sha256 = SHA256.Create()) // Crear SHA256 una vez para optimizar
        {
            writer.WriteLine("Iteración,Tiempo Generación Claves (ms),Tiempo Creación Firma (ms),Tiempo Verificación Firma (ms),Tiempo Total (ms)");

            // Inicializamos las listas para almacenar los tiempos
            var tiemposGeneracionClaves = new System.Collections.Generic.List<double>();
            var tiemposCreacionFirma = new System.Collections.Generic.List<double>();
            var tiemposVerificacionFirma = new System.Collections.Generic.List<double>();
            var tiemposTotales = new System.Collections.Generic.List<double>();

            for (int i = 0; i < nIterations; i++)
            {
                try
                {
                    // 1. Generación de claves RSA
                    var stopwatch = Stopwatch.StartNew();
                    RSAParameters privateKey;
                    RSAParameters publicKey;
                    using (var rsa = RSA.Create())
                    {
                        rsa.KeySize = bits;
                        privateKey = rsa.ExportParameters(true);
                        publicKey = rsa.ExportParameters(false);
                    }
                    stopwatch.Stop();
                    double tiempoGeneracion = stopwatch.Elapsed.TotalMilliseconds;
                    tiemposGeneracionClaves.Add(tiempoGeneracion);

                    // 2. Creación de una firma
                    byte[] mensaje = System.Text.Encoding.UTF8.GetBytes("Este es un mensaje de prueba para firmar.");
                    byte[] firma;
                    stopwatch.Restart();
                    using (var rsa = RSA.Create())
                    {
                        rsa.ImportParameters(privateKey);
                        firma = rsa.SignData(mensaje, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                    }
                    stopwatch.Stop();
                    double tiempoFirma = stopwatch.Elapsed.TotalMilliseconds;
                    tiemposCreacionFirma.Add(tiempoFirma);

                    // 3. Verificación de la firma
                    stopwatch.Restart();
                    using (var rsa = RSA.Create())
                    {
                        rsa.ImportParameters(publicKey);
                        bool esValida = rsa.VerifyData(mensaje, firma, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                        if (!esValida)
                        {
                            Console.WriteLine($"Advertencia: Firma no válida en la iteración {i + 1}");
                        }
                    }
                    stopwatch.Stop();
                    double tiempoVerificacion = stopwatch.Elapsed.TotalMilliseconds;
                    tiemposVerificacionFirma.Add(tiempoVerificacion);

                    // Calcular el tiempo total
                    double tiempoTotal = tiempoGeneracion + tiempoFirma + tiempoVerificacion;
                    tiemposTotales.Add(tiempoTotal);

                    // Escribir los resultados de cada iteración en el archivo CSV
                    writer.WriteLine($"{i + 1},{tiempoGeneracion:F3},{tiempoFirma:F3},{tiempoVerificacion:F3},{tiempoTotal:F3}");

                    //Console.WriteLine($"Iteración {i + 1} completada.");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error en la iteración {i + 1}: {ex.Message}");
                }
            }

            // Calcular y mostrar resultados promedio
            double promedioGeneracionClaves = Promedio(tiemposGeneracionClaves);
            double promedioCreacionFirma = Promedio(tiemposCreacionFirma);
            double promedioVerificacionFirma = Promedio(tiemposVerificacionFirma);
            double promedioTotal = Promedio(tiemposTotales);

            double desviacionGeneracionClaves = DesviacionEstandar(tiemposGeneracionClaves);
            double desviacionCreacionFirma = DesviacionEstandar(tiemposCreacionFirma);
            double desviacionVerificacionFirma = DesviacionEstandar(tiemposVerificacionFirma);
            double desviacionTotal = DesviacionEstandar(tiemposTotales);

            Console.WriteLine($"\nResultados promedio para {nIterations} iteraciones:");
            Console.WriteLine($"Tiempo de generación de claves: {promedioGeneracionClaves:F3} ms (Desviación estándar: {desviacionGeneracionClaves:F3} ms)");
            Console.WriteLine($"Tiempo de creación de la firma: {promedioCreacionFirma:F3} ms (Desviación estándar: {desviacionCreacionFirma:F3} ms)");
            Console.WriteLine($"Tiempo de verificación de la firma: {promedioVerificacionFirma:F3} ms (Desviación estándar: {desviacionVerificacionFirma:F3} ms)");
            Console.WriteLine($"Tiempo total de ejecución: {promedioTotal:F3} ms (Desviación estándar: {desviacionTotal:F3} ms)");
        }
    }

    // Función para calcular el promedio
    static double Promedio(System.Collections.Generic.List<double> lista)
    {
        double suma = 0;
        foreach (var valor in lista)
        {
            suma += valor;
        }
        return suma / lista.Count;
    }

    // Función para calcular la desviación estándar
    static double DesviacionEstandar(System.Collections.Generic.List<double> lista)
    {
        double promedio = Promedio(lista);
        double sumaCuadrados = 0;
        foreach (var valor in lista)
        {
            sumaCuadrados += Math.Pow(valor - promedio, 2);
        }
        return Math.Sqrt(sumaCuadrados / (lista.Count - 1));
    }
}
