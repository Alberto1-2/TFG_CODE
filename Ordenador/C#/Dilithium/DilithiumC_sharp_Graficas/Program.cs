using Org.BouncyCastle.Pqc.Crypto.Crystals.Dilithium;
using Org.BouncyCastle.Security;
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;

namespace DilithiumC_sharp_Graficas
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                // Configuración para usar "." en vez de ","
                CultureInfo.DefaultThreadCurrentCulture = new CultureInfo("en-US");
                CultureInfo.DefaultThreadCurrentUICulture = new CultureInfo("en-US");

                var msg = "Hola, estamos en pruebas con el algoritmo pqc Crystals Dilithium";
                int iterations = 1000; // Número de repeticiones

                var versions = new[] { "Dilithium2", "Dilithium3", "Dilithium5" };
                foreach (var version in versions)
                {
                    Console.WriteLine($"Ejecutando pruebas para {version}...");
                    RunDilithiumTests(version, msg, iterations);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("Error: " + e.Message);
            }
        }

        static void RunDilithiumTests(string method, string msg, int iterations)
        {
            var random = new SecureRandom();
            DilithiumKeyGenerationParameters keyGenParameters = method switch
            {
                "Dilithium3" => new DilithiumKeyGenerationParameters(random, DilithiumParameters.Dilithium3),
                "Dilithium5" => new DilithiumKeyGenerationParameters(random, DilithiumParameters.Dilithium5),
                _ => new DilithiumKeyGenerationParameters(random, DilithiumParameters.Dilithium2),
            };

            var keyPairGen = new DilithiumKeyPairGenerator();
            keyPairGen.Init(keyGenParameters);

            var keyGenTimes = new List<double>();
            var signTimes = new List<double>();
            var verifyTimes = new List<double>();
            double totalKeyGenTime = 0, totalSignTime = 0, totalVerifyTime = 0;

            // Crear una lista para almacenar los resultados
            var results = new List<string>();

            // Agregar la cabecera solo una vez
            results.Add("Iteración,Dilithium Version,Tiempo Generación Claves,Tiempo Firma,Tiempo Verificación,Tiempo Total");

            // Ejecutamos una iteración para que cargue los recursos
            var warmupkeyPair = keyPairGen.GenerateKeyPair();
            var warmuppubKey = (DilithiumPublicKeyParameters)warmupkeyPair.Public;
            var warmupprivKey = (DilithiumPrivateKeyParameters)warmupkeyPair.Private;

            // Firmar
            var warmupaliceSign = new DilithiumSigner();
            warmupaliceSign.Init(true, warmupprivKey);
            var warmupsignature = warmupaliceSign.GenerateSignature(System.Text.Encoding.UTF8.GetBytes(msg));

            // Verificar firma
            var warmupbobVerify = new DilithiumSigner();
            warmupbobVerify.Init(false, warmuppubKey);
            var warmuprtn = warmupbobVerify.VerifySignature(System.Text.Encoding.UTF8.GetBytes(msg), warmupsignature);


            for (int i = 0; i < iterations; i++)
            {
                // Medir tiempo de generación de claves
                var sw = Stopwatch.StartNew();
                var keyPair = keyPairGen.GenerateKeyPair();
                sw.Stop();
                var keyGenTime = sw.Elapsed.TotalMilliseconds;
                keyGenTimes.Add(keyGenTime);
                totalKeyGenTime += keyGenTime;

                var pubKey = (DilithiumPublicKeyParameters)keyPair.Public;
                var privKey = (DilithiumPrivateKeyParameters)keyPair.Private;

                // Firmar
                var aliceSign = new DilithiumSigner();
                aliceSign.Init(true, privKey);

                sw.Restart();
                var signature = aliceSign.GenerateSignature(System.Text.Encoding.UTF8.GetBytes(msg));
                sw.Stop();
                var signTime = sw.Elapsed.TotalMilliseconds;
                signTimes.Add(signTime);
                totalSignTime += signTime;

                // Verificar firma
                var bobVerify = new DilithiumSigner();
                bobVerify.Init(false, pubKey);

                sw.Restart();
                var rtn = bobVerify.VerifySignature(System.Text.Encoding.UTF8.GetBytes(msg), signature);
                sw.Stop();
                var verifyTime = sw.Elapsed.TotalMilliseconds;
                verifyTimes.Add(verifyTime);
                totalVerifyTime += verifyTime;

                // Calcular tiempo total
                var totalTime = keyGenTime + signTime + verifyTime;

                // Guardar los resultados en la lista
                results.Add($"{i + 1},{method},{keyGenTime:F4},{signTime:F4},{verifyTime:F4},{totalTime:F4}");
            }

            var csvFileName = $"{method}_performance.csv";
            File.WriteAllLines(csvFileName, results);
            Console.WriteLine($"Resultados exportados a '{csvFileName}'.");

            // Calcular estadísticas
            PrintStatistics("Generación de Claves", keyGenTimes);
            PrintStatistics("Firma", signTimes);
            PrintStatistics("Verificación", verifyTimes);

            // Mostrar tiempos promedios
            Console.WriteLine($"Para {iterations} iteraciones ");
            Console.WriteLine($"Para {method} ");
            Console.WriteLine("Promedio de tiempo de generación de claves: {0:F4} ms", (double)totalKeyGenTime / iterations);
            Console.WriteLine("Promedio de tiempo de firma: {0:F4} ms", (double)totalSignTime / iterations);
            Console.WriteLine("Promedio de tiempo de verificación: {0:F4} ms", (double)totalVerifyTime / iterations);
            Console.WriteLine("-----------------------------------------------------------");
        }

        static void PrintStatistics(string operation, List<double> times)
        {
            var avg = times.Average();
            var stdDev = CalculateStdDev(times, avg);

            // Mostrar estadísticas solo al final
            Console.WriteLine($"--- Estadísticas para {operation} ---");
            Console.WriteLine("Promedio: {0:F4} ms", avg);
            Console.WriteLine("Desviación Estándar: {0:F4} ms", stdDev);
            Console.WriteLine("-------------------------------------");
        }

        static double CalculateStdDev(List<double> times, double mean)
        {
            var variance = times.Average(t => Math.Pow(t - mean, 2));
            return Math.Sqrt(variance);
        }
    }
}
