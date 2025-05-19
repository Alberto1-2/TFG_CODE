using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Org.BouncyCastle.Pqc.Crypto.Falcon;
using Org.BouncyCastle.Security;
using System.Globalization;

namespace falcon_c_sharp
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

                // Configuración inicial
                var smallMsg = "Pruebas de Falcon en C#";
                var largeMsg = new string('A', 10000); // Mensaje grande de 10,000 caracteres

                if (args.Length > 0) smallMsg = args[0];

                // Lista de versiones de Falcon a probar
                var versiones = new[] { "Falcon512", "Falcon1024" };

                // Lista para estadísticas globales
                var resultadosGlobales = new List<ResultadoGlobal>();

                foreach (var version in versiones)
                {
                    Console.WriteLine($"--- Ejecutando pruebas para {version} ---");

                    // Configurar parámetros de Falcon
                    var random = new SecureRandom();
                    var keyGenParameters = version switch
                    {
                        "Falcon1024" => new FalconKeyGenerationParameters(random, FalconParameters.falcon_1024),
                        _ => new FalconKeyGenerationParameters(random, FalconParameters.falcon_512),
                    };

                    // Pruebas de rendimiento para mensajes pequeños y grandes
                    resultadosGlobales.Add(RealizarPruebas(smallMsg, keyGenParameters, "pequeño", version));
                    resultadosGlobales.Add(RealizarPruebas(largeMsg, keyGenParameters, "grande", version));
                }

                // Exportar resultados globales a un archivo CSV
                var globalCsvFileName = "Falcon_Global_Stats.csv";
                using (var writer = new StreamWriter(globalCsvFileName))
                {
                    writer.WriteLine("Versión,Tamaño Mensaje,Generación Claves,Firma,Verificación");
                    foreach (var resultado in resultadosGlobales)
                    {
                        writer.WriteLine(
                            $"{resultado.Version},{resultado.TamañoMensaje}," +
                            $"{resultado.PromedioGeneracion:F4} ms (+-{resultado.DesviacionGeneracion:F4})," +
                            $"{resultado.PromedioFirma:F4} ms (+-{resultado.DesviacionFirma:F4})," +
                            $"{resultado.PromedioVerificacion:F4} ms (+-{resultado.DesviacionVerificacion:F4})");
                    }
                }

                Console.WriteLine($"Resultados globales exportados a '{globalCsvFileName}'.");
            }
            catch (Exception e)
            {
                Console.WriteLine("Error: {0}", e.Message);
            }
        }

        static ResultadoGlobal RealizarPruebas(string mensaje, FalconKeyGenerationParameters keyGenParameters, string tamañoMensaje, string metodo)
        {
            // Listas para almacenar los tiempos
            var tiemposGeneracion = new List<double>();
            var tiemposFirma = new List<double>();
            var tiemposVerificacion = new List<double>();
            int repeticiones = 1000; // Número de iteraciones

            // Archivo CSV para resultados detallados
            var csvFileName = $"{metodo}_{tamañoMensaje}_performance.csv";
            using (var writer = new StreamWriter(csvFileName))
            {
                writer.WriteLine("Iteración,Falcon Version,Tamaño Mensaje,Tiempo Generación Claves,Tiempo Firma,Tiempo Verificación,Tiempo Total");

                for (int i = 0; i < repeticiones; i++)
                {
                    // Generación de claves
                    var sw = Stopwatch.StartNew();
                    var keyPairGen = new FalconKeyPairGenerator();
                    keyPairGen.Init(keyGenParameters);
                    var keyPair = keyPairGen.GenerateKeyPair();
                    sw.Stop();
                    var tiempoGen = sw.Elapsed.TotalMilliseconds;
                    tiemposGeneracion.Add(tiempoGen);

                    var pubKey = (FalconPublicKeyParameters)keyPair.Public;
                    var privKey = (FalconPrivateKeyParameters)keyPair.Private;

                    // Firma
                    var signer = new FalconSigner();
                    signer.Init(true, privKey);
                    sw.Restart();
                    var signature = signer.GenerateSignature(System.Text.Encoding.UTF8.GetBytes(mensaje));
                    sw.Stop();
                    var tiempoFirma = sw.Elapsed.TotalMilliseconds;
                    tiemposFirma.Add(tiempoFirma);

                    // Verificación de la firma
                    var verifier = new FalconSigner();
                    verifier.Init(false, pubKey);
                    sw.Restart();
                    var resultado = verifier.VerifySignature(System.Text.Encoding.UTF8.GetBytes(mensaje), signature);
                    sw.Stop();
                    var tiempoVerificacion = sw.Elapsed.TotalMilliseconds;
                    tiemposVerificacion.Add(tiempoVerificacion);

                    if (!resultado)
                    {
                        Console.WriteLine("Error: la firma no fue verificada correctamente.");
                        return null;
                    }

                    // Calcular tiempo total
                    var tiempoTotal = tiempoGen + tiempoFirma + tiempoVerificacion;

                    // Guardar en CSV
                    writer.WriteLine($"{i + 1},{metodo},{tamañoMensaje},{tiempoGen:F4},{tiempoFirma:F4},{tiempoVerificacion:F4},{tiempoTotal:F4}");
                }
            }

            Console.WriteLine($"Resultados exportados a '{csvFileName}'.");

            // Calcular promedios y desviaciones
            var promedioGen = tiemposGeneracion.Average();
            var promedioFirma = tiemposFirma.Average();
            var promedioVerif = tiemposVerificacion.Average();
            var desviacionGen = CalcularDesviacionEstandar(tiemposGeneracion, promedioGen);
            var desviacionFirma = CalcularDesviacionEstandar(tiemposFirma, promedioFirma);
            var desviacionVerif = CalcularDesviacionEstandar(tiemposVerificacion, promedioVerif);

            // Mostrar estadísticas
            MostrarEstadisticas("Generación de Claves", tiemposGeneracion);
            MostrarEstadisticas("Firma", tiemposFirma);
            MostrarEstadisticas("Verificación", tiemposVerificacion);

            // Retornar los promedios y desviaciones como resultado global
            return new ResultadoGlobal
            {
                Version = metodo,
                TamañoMensaje = tamañoMensaje,
                PromedioGeneracion = promedioGen,
                DesviacionGeneracion = desviacionGen,
                PromedioFirma = promedioFirma,
                DesviacionFirma = desviacionFirma,
                PromedioVerificacion = promedioVerif,
                DesviacionVerificacion = desviacionVerif
            };
        }

        static void MostrarEstadisticas(string operacion, List<double> tiempos)
        {
            var promedio = tiempos.Average();
            var desviacion = CalcularDesviacionEstandar(tiempos, promedio);

            Console.WriteLine($"--- Estadísticas para {operacion} ---");
            Console.WriteLine($"Promedio: {promedio:F4} ms");
            Console.WriteLine($"Desviación Estándar: {desviacion:F4} ms");
            Console.WriteLine("-------------------------------------");
        }

        static double CalcularDesviacionEstandar(List<double> tiempos, double promedio)
        {
            var varianza = tiempos.Average(t => Math.Pow(t - promedio, 2));
            return Math.Sqrt(varianza);
        }
    }

    // Clase para almacenar resultados globales
    class ResultadoGlobal
    {
        public string Version { get; set; }
        public string TamañoMensaje { get; set; }
        public double PromedioGeneracion { get; set; }
        public double DesviacionGeneracion { get; set; }
        public double PromedioFirma { get; set; }
        public double DesviacionFirma { get; set; }
        public double PromedioVerificacion { get; set; }
        public double DesviacionVerificacion { get; set; }
    }
}
