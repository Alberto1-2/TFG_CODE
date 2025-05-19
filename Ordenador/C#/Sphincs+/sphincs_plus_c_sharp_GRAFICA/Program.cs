using Org.BouncyCastle.Pqc.Crypto.SphincsPlus;
using Org.BouncyCastle.Security;
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;

namespace SphincsPlus_c_sharp
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                // Configuración cultural para separar decimales con "."
                CultureInfo.DefaultThreadCurrentCulture = new CultureInfo("en-US");
                CultureInfo.DefaultThreadCurrentUICulture = new CultureInfo("en-US");
                

                var msg = "Probando con el algoritmo pqc Sphincs+";
                int iterations = 100; // Número de iteraciones

                var versions = new[]
                {
                    SphincsPlusParameters.shake_128s,
                    SphincsPlusParameters.shake_128f,
                    SphincsPlusParameters.shake_192s,
                    SphincsPlusParameters.shake_192f,
                    SphincsPlusParameters.shake_256s,
                    SphincsPlusParameters.shake_256f
                };

                foreach (var version in versions)
                {
                    Console.WriteLine($"Ejecutando pruebas para {version.Name}...");
                    RunSphincsPlusTests(version, msg, iterations);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("Error: {0}", e.Message);
            }
        }

        static void RunSphincsPlusTests(SphincsPlusParameters parameters, string msg, int iterations)
        {
            var random = new SecureRandom();
            var keyGenParameters = new SphincsPlusKeyGenerationParameters(random, parameters);
            var keyPairGen = new SphincsPlusKeyPairGenerator();
            keyPairGen.Init(keyGenParameters);

            var keyGenTimes = new List<double>();
            var signTimes = new List<double>();
            var verifyTimes = new List<double>();
            double totalKeyGenTime = 0, totalSignTime = 0, totalVerifyTime = 0;

            // Crear archivo CSV para exportar los datos
            var csvFileName = $"{parameters.Name}_performanceShake.csv";
            using (var writer = new StreamWriter(csvFileName))
            {
                writer.WriteLine("Iteración,SPHINCS+ Version,Tiempo Generación Claves,Tiempo Firma,Tiempo Verificación,Tiempo Total");

                for (int i = 0; i < iterations; i++)
                {
                    // Medir tiempo de generación de claves
                    var sw = Stopwatch.StartNew();
                    var keyPair = keyPairGen.GenerateKeyPair();
                    sw.Stop();
                    var keyGenTime = sw.Elapsed.TotalMilliseconds;
                    keyGenTimes.Add(keyGenTime);
                    totalKeyGenTime += keyGenTime;

                    var pubKey = (SphincsPlusPublicKeyParameters)keyPair.Public;
                    var privKey = (SphincsPlusPrivateKeyParameters)keyPair.Private;

                    // Firmar
                    var aliceSign = new SphincsPlusSigner();
                    aliceSign.Init(true, privKey);

                    sw.Restart();
                    var signature = aliceSign.GenerateSignature(System.Text.Encoding.UTF8.GetBytes(msg));
                    sw.Stop();
                    var signTime = sw.Elapsed.TotalMilliseconds;
                    signTimes.Add(signTime);
                    totalSignTime += signTime;

                    // Verificar firma
                    var bobVerify = new SphincsPlusSigner();
                    bobVerify.Init(false, pubKey);

                    sw.Restart();
                    var rtn = bobVerify.VerifySignature(System.Text.Encoding.UTF8.GetBytes(msg), signature);
                    sw.Stop();
                    var verifyTime = sw.Elapsed.TotalMilliseconds;
                    verifyTimes.Add(verifyTime);
                    totalVerifyTime += verifyTime;

                    // Calcular tiempo total
                    var totalTime = keyGenTime + signTime + verifyTime;

                    // Guardar resultados en el archivo CSV
                    writer.WriteLine($"{i + 1},{parameters.Name},{keyGenTime:F4},{signTime:F4},{verifyTime:F4},{totalTime:F4}");
                }
            }

            Console.WriteLine($"Resultados exportados a '{csvFileName}'.");

            // Calcular estadísticas
            PrintStatistics("Generación de Claves", keyGenTimes);
            PrintStatistics("Firma", signTimes);
            PrintStatistics("Verificación", verifyTimes);

            // Mostrar tiempos promedio
            Console.WriteLine($"Para {iterations} iteraciones");
            Console.WriteLine($"Para {parameters.Name}");
            Console.WriteLine("Promedio de tiempo de generación de claves: {0:F4} ms", totalKeyGenTime / iterations);
            Console.WriteLine("Promedio de tiempo de firma: {0:F4} ms", totalSignTime / iterations);
            Console.WriteLine("Promedio de tiempo de verificación: {0:F4} ms", totalVerifyTime / iterations);
            Console.WriteLine("-----------------------------------------------------------");
        }

        static void PrintStatistics(string operation, List<double> times)
        {
            var avg = times.Average();
            var stdDev = CalculateStdDev(times, avg);

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
