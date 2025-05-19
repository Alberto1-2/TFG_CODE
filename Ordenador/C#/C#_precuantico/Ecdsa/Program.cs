using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;

class ECDSA
{
    static void Main(string[] args)
    {
        // Parámetros para las pruebas
        int nIterations = 1000;

        // Medir el rendimiento para claves de 256 y 384 bits
        //MedirRendimiento(256, nIterations, "ecdsa_256.csv");
        MedirRendimiento(384, nIterations, "ecdsa1_384.csv");
    }

    
    // Función para medir el rendimiento de la generación de claves, creación y verificación de firmas
    static void MedirRendimiento(int bits, int nIterations, string filename)
    {
        // WARMUP DE CALENTAMIENTO
        byte[] firmaGeneradaWarmup; // Variable usada en la firma y verificación
        // 1. Generación de claves ECDSA
        using (var ecdsaWarmup = ECDsa.Create(bits == 256 ? ECCurve.NamedCurves.nistP256 : ECCurve.NamedCurves.nistP384))
        {
            // Generar la clave pública y privada
            var privateKey = ecdsaWarmup.ExportParameters(true);
            var publicKey = ecdsaWarmup.ExportParameters(false);
        }

        // 2. Creación de una firma
        byte[] mensajeWarmup = System.Text.Encoding.UTF8.GetBytes("Este es un mensaje de prueba para firmar.");
        using (var ecdsaWarmup = ECDsa.Create(bits == 256 ? ECCurve.NamedCurves.nistP256 : ECCurve.NamedCurves.nistP384))
        {
            firmaGeneradaWarmup = ecdsaWarmup.SignData(mensajeWarmup, HashAlgorithmName.SHA256);
        }

        // 3. Verificación de la firma
        if (firmaGeneradaWarmup != null) // Asegurarnos de que la firma no sea nula
        {
            using (var ecdsaWarmup = ECDsa.Create(bits == 256 ? ECCurve.NamedCurves.nistP256 : ECCurve.NamedCurves.nistP384))
            {
                bool esValida = ecdsaWarmup.VerifyData(mensajeWarmup, firmaGeneradaWarmup, HashAlgorithmName.SHA256);
            }
        }

        // Configuración cultural para separar decimales con "."
        CultureInfo.DefaultThreadCurrentCulture = new CultureInfo("en-US");
        CultureInfo.DefaultThreadCurrentUICulture = new CultureInfo("en-US");

        Console.WriteLine($"\nIniciando pruebas para claves ECDSA de {bits} bits...");

        // Crear el archivo CSV
        using (var writer = new StreamWriter(filename))
        {
            writer.WriteLine("Iteración,Tiempo Generación de Claves (ms),Tiempo Creación de Firma (ms),Tiempo Verificación de Firma (ms),Tiempo Total (ms)");

            // Inicializamos las listas para almacenar los tiempos
            var tiemposGeneracionClaves = new System.Collections.Generic.List<double>();
            var tiemposCreacionFirma = new System.Collections.Generic.List<double>();
            var tiemposVerificacionFirma = new System.Collections.Generic.List<double>();
            var tiemposTotales = new System.Collections.Generic.List<double>();

            byte[] firmaGenerada; // Variable fuera del bucle para usar en la verificación

            for (int i = 0; i < nIterations; i++)
            {
                // 1. Generación de claves ECDSA
                var stopwatch = Stopwatch.StartNew();
                using (var ecdsa = ECDsa.Create(bits == 256 ? ECCurve.NamedCurves.nistP256 : ECCurve.NamedCurves.nistP384))
                {
                    // Generar la clave pública y privada
                    var privateKey = ecdsa.ExportParameters(true);
                    var publicKey = ecdsa.ExportParameters(false);
                }
                stopwatch.Stop();
                double tiempoGeneracionClavesIter = stopwatch.Elapsed.TotalMilliseconds;
                tiemposGeneracionClaves.Add(tiempoGeneracionClavesIter);

                // 2. Creación de una firma
                byte[] mensaje = System.Text.Encoding.UTF8.GetBytes("Este es un mensaje de prueba para firmar.");
                stopwatch.Restart();
                using (var ecdsa = ECDsa.Create(bits == 256 ? ECCurve.NamedCurves.nistP256 : ECCurve.NamedCurves.nistP384))
                {
                    firmaGenerada = ecdsa.SignData(mensaje, HashAlgorithmName.SHA256);
                }
                stopwatch.Stop();
                double tiempoCreacionFirmaIter = stopwatch.Elapsed.TotalMilliseconds;
                tiemposCreacionFirma.Add(tiempoCreacionFirmaIter);

                // 3. Verificación de la firma
                if (firmaGenerada != null) // Asegurarnos de que la firma no sea nula
                {
                    stopwatch.Restart();
                    using (var ecdsa = ECDsa.Create(bits == 256 ? ECCurve.NamedCurves.nistP256 : ECCurve.NamedCurves.nistP384))
                    {
                        bool esValida = ecdsa.VerifyData(mensaje, firmaGenerada, HashAlgorithmName.SHA256);
                    }
                    stopwatch.Stop();
                    double tiempoVerificacionFirmaIter = stopwatch.Elapsed.TotalMilliseconds;
                    tiemposVerificacionFirma.Add(tiempoVerificacionFirmaIter);
                }
                else
                {
                    // Si la firma es nula, asignar un valor de tiempo por defecto (puede ajustarse según se desee)
                    tiemposVerificacionFirma.Add(0);
                }

                // Calcular el tiempo total (suma de todos los tiempos)
                double tiempoTotalIter = tiempoGeneracionClavesIter + tiempoCreacionFirmaIter + (firmaGenerada != null ? tiemposVerificacionFirma[tiemposVerificacionFirma.Count - 1] : 0);
                tiemposTotales.Add(tiempoTotalIter);

                // Escribir los resultados de cada iteración en el archivo CSV
                writer.WriteLine($"{i + 1},{tiempoGeneracionClavesIter:F3},{tiempoCreacionFirmaIter:F3},{tiemposVerificacionFirma[tiemposVerificacionFirma.Count - 1]:F3},{tiempoTotalIter:F3}");

                //Console.WriteLine($"Iteración {i + 1} completada.");
            }

            // Calcular los tiempos promedio
            double promedioGeneracionClaves = Promedio(tiemposGeneracionClaves);
            double promedioCreacionFirma = Promedio(tiemposCreacionFirma);
            double promedioVerificacionFirma = Promedio(tiemposVerificacionFirma);
            double promedioTotal = Promedio(tiemposTotales);

            // Calcular la desviación estándar
            double desviacionGeneracionClaves = DesviacionEstandar(tiemposGeneracionClaves);
            double desviacionCreacionFirma = DesviacionEstandar(tiemposCreacionFirma);
            double desviacionVerificacionFirma = DesviacionEstandar(tiemposVerificacionFirma);
            double desviacionTotal = DesviacionEstandar(tiemposTotales);

            // Mostrar resultados
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
