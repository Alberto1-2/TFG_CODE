using Org.BouncyCastle.Pqc.Crypto.Crystals.Kyber;
using Org.BouncyCastle.Security;
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;

namespace MiproyectoC_sharp_Graficas
{
    class Program
    {
        static void Main(string[] args)
        {
            // Establecer la cultura a en-US para asegurar el uso de puntos como separador decimal
            CultureInfo.DefaultThreadCurrentCulture = new CultureInfo("en-US");
            CultureInfo.DefaultThreadCurrentUICulture = new CultureInfo("en-US");

            // Opciones posibles en Kyber
            var validSizes = new[] { "kyber512", "kyber768", "kyber1024" };

            // Iterar todas las versiones de Kyber
            foreach (var size in validSizes)
            {
                Console.WriteLine("\nEjecutando pruebas para Kyber-{0}...", size);
                RunTests(size, 1000); // Ejecutamos 1000 iteraciones de cada tamaño de Kyber
            }

            Console.WriteLine("\nPruebas completadas.");
        }

        static void RunTests(string size, int iterations)
        {
            var random = new SecureRandom();
            KyberKeyGenerationParameters keyGenParameters = size switch
            {
                "kyber512" => new KyberKeyGenerationParameters(random, KyberParameters.kyber512),
                "kyber768" => new KyberKeyGenerationParameters(random, KyberParameters.kyber768),
                "kyber1024" => new KyberKeyGenerationParameters(random, KyberParameters.kyber1024),
                _ => throw new ArgumentException("Invalid size"),
            };

            var kyberKeyPairGenerator = new KyberKeyPairGenerator();
            kyberKeyPairGenerator.Init(keyGenParameters);

             // "Calentamiento" (warm-up) para cargar recursos antes de medir
            var warmupKeyPair = kyberKeyPairGenerator.GenerateKeyPair();
            var warmupPublic = (KyberPublicKeyParameters)warmupKeyPair.Public;
            var warmupPrivate = (KyberPrivateKeyParameters)warmupKeyPair.Private;

            var bobWarmup = new KyberKemGenerator(random);
            var warmupEncapsulated = bobWarmup.GenerateEncapsulated(warmupPublic);
            var warmupCipherText = warmupEncapsulated.GetEncapsulation();

            var aliceWarmup = new KyberKemExtractor(warmupPrivate);
            var warmupSecret = aliceWarmup.ExtractSecret(warmupCipherText);


            // Abrir archivo CSV para escribir los resultados
            using (var writer = new StreamWriter($"{size}_performance.csv"))
            {
                // Escribir cabecera
                writer.WriteLine("Iteración,Kyber Version,Tiempo Generación Claves,Tiempo Encapsulación,Tiempo Decapsulación,Tiempo Total");

                var keyGenTimes = new List<double>();
                var encapsTimes = new List<double>();
                var extractTimes = new List<double>();
                var totalTimes = new List<double>();

                for (int i = 0; i < iterations; i++)
                {
                    // Medir tiempo de generación de claves
                    var sw = Stopwatch.StartNew();
                    var aKeyPair = kyberKeyPairGenerator.GenerateKeyPair();
                    var aPublic = (KyberPublicKeyParameters)aKeyPair.Public;
                    var aPrivate = (KyberPrivateKeyParameters)aKeyPair.Private;
                    sw.Stop();
                    keyGenTimes.Add(sw.Elapsed.TotalMilliseconds);

                    // Encapsular secreto
                    var bobKyberKemGenerator = new KyberKemGenerator(random);
                    sw.Restart();
                    var encapsulatedSecret = bobKyberKemGenerator.GenerateEncapsulated(aPublic);
                    var cipherText = encapsulatedSecret.GetEncapsulation();
                    sw.Stop();
                    encapsTimes.Add(sw.Elapsed.TotalMilliseconds);

                    // Extraer secreto
                    var aliceKemExtractor = new KyberKemExtractor(aPrivate);
                    sw.Restart();
                    var aliceSecret = aliceKemExtractor.ExtractSecret(cipherText);
                    sw.Stop();
                    extractTimes.Add(sw.Elapsed.TotalMilliseconds);

                    // Tiempo total de esta iteración
                    totalTimes.Add(keyGenTimes.Last() + encapsTimes.Last() + extractTimes.Last());

                    // Escribir los datos de esta iteración en el archivo CSV
                    writer.WriteLine($"{i + 1},{size},{keyGenTimes.Last():F4},{encapsTimes.Last():F4},{extractTimes.Last():F4},{totalTimes.Last():F4}");
                }

                // Calcular promedios y desviaciones estándar
                var avgKeyGen = keyGenTimes.Average();
                var stdKeyGen = CalculateStdDev(keyGenTimes, avgKeyGen);

                var avgEncaps = encapsTimes.Average();
                var stdEncaps = CalculateStdDev(encapsTimes, avgEncaps);

                var avgExtract = extractTimes.Average();
                var stdExtract = CalculateStdDev(extractTimes, avgExtract);

                var avgTotal = totalTimes.Average();
                var stdTotal = CalculateStdDev(totalTimes, avgTotal);

                // Mostrar los resultados
                Console.WriteLine("Kyber-{0} resultados:", size);
                Console.WriteLine("Promedio Generación Claves: {0:F4} ms (+/- {1:F4})", avgKeyGen, stdKeyGen);
                Console.WriteLine("Promedio Encapsulación: {0:F4} ms (+/- {1:F4})", avgEncaps, stdEncaps);
                Console.WriteLine("Promedio Decapsulación: {0:F4} ms (+/- {1:F4})", avgExtract, stdExtract);
                Console.WriteLine("Promedio Total: {0:F4} ms (+/- {1:F4})", avgTotal, stdTotal);
            }

            Console.WriteLine($"Datos exportados a '{size}_performance.csv'.");
        }

        static double CalculateStdDev(List<double> values, double mean)
        {
            return Math.Sqrt(values.Sum(v => Math.Pow(v - mean, 2)) / values.Count);
        }
    }
}
