# TFG_CODE
## Análisis de Algoritmos Post-Cuánticos de Cifrado
Este repositorio contiene el código desarrollado para mi Trabajo Fin de Grado en Ingeniería Informática (Universidad Autónoma de Madrid), centrado en el análisis de rendimiento de algoritmos criptográficos post-cuánticos en distintos lenguajes y plataformas.

## Objetivo del proyecto
Evaluar y comparar el rendimiento de distintos algoritmos criptográficos post-cuánticos seleccionados por el NIST en términos de:
- Generación de claves
- Cifrado / descifrado
- Firmado / verificación

El análisis se realiza en distintos entornos de ejecución incluyendo ordenador de escritorio, dispositivo móvil y Raspberry Pi.

## Algoritmos analizados
- Kyber (KEM)
- Dilithium (firma digital)
- FALCON (firma digital)
- SPHINCS+ (firma digital)

## Tecnologías utilizadas
- **Lenguajes**: C, Python, Java, C# y Kotlin
- **Entornos**: Linux, Android, Raspberry Pi
- **Bibliotecas**:
  - Implementaciones oficiales NIST-PQC
  - Bouncy Castle
- Generación de resultados y gráficas con el diagrama de cajas (box plot) mediante python y matplotlib.

- ## Organización del repositorio
El repositorio contiene los ficheros modificados o desarrollados para la realización de las pruebas.

** En los casos de C y Python es necesario clonar previamente los repositorios oficiales de referencia indicados en el código.  
** Para Java y C# se requiere la instalación de la biblioteca Bouncy Castle.

## Procesos realizados
- Diseño y adaptación de pruebas de rendimiento
- Integración de múltiples implementaciones post-cuánticas
- Ejecución de benchmarks en diferentes plataformas
- Análisis y comparación de resultados

## Ejecución
Cada lenguaje requiere su entorno correspondiente:
- Java: JDK + Bouncy Castle
- C#: .NET SDK
- C/Python: repositorios oficiales indicados en el código

### Información Adicional: 
Para los lenguajes de Python y C en los algoritmos post-cuánticos se utilizan las versiones de referencia oficial (en C, para Kyber (https://pq-crystals.org/kyber/) y Dilithium [https://pq-crystals.org/dilithium/] con pq-crystals y SPHINCS+ [https://sphincs.org/index.html] con SPHINCS) o 
elaboradas (en C con DIGITAL SIGNATURES NIST-PQC ROUND3 BENCHMARKS para FALCON [https://github.com/josscimat/DIGITAL_SIGNATURES_NIST-PQC_ROUND3_BENCHMARKS] 
y de la referencia oficial [https://falcon-sign.info/impl/falcon.h.html] y Kyber para Raspberry con optimizaciones de NEON [https://github.com/cothan/kyber],
en Python, Kyber-py [https://github.com/GiacomoPope/kyber-py] para Kyber, Dilithium-py [https://github.com/GiacomoPope/dilithium-py] para diltihium,
FALCON.py [https://github.com/tprest/falcon.py] de FALCON-sign para FALCON y con asecuritysite para SPHINCS+ [https://asecuritysite.com/slh_dsa/fips205]). 

Para los lenguajes de C# y Java, se han diseñado a partir de la web https://asecuritysite.com/ y de la biblioteca de Bouncy Castle.

** Solo se proporcionan los ficheros que se han modificado para realizar la pruebas, en el caso de C y Python habría que clonar los repositorios indicados, y en Java y C#, instalar la librería de Bouncy Castle, junto a las herramientas de desarrollo para trabajar con ambos lenguajes (Java (JDK) y .NET SDK respectivamente)

** Por simplificación, en Raspberry Pi 5, se muestra el código en C, para el resto de lenguajes utilizar los códigos disponibles en la carpeta Ordenador (modificando únicamente el nombre de los ficheros .csv y/o gráficas que se generen, y pudiendo modificar las ejecuciones para ejecutar 1 o más versiones del algoritmo, p.ej en RSA en C#: // Medir el rendimiento para claves de 2048 y 4096 bits
        //MedirRendimiento(2048, nIterations, "rsa1_2048.csv");
        MedirRendimiento(4096, nIterations, "rsa2_4096.csv");). 
        
        Se puede decidir si ejecutar por separado o todo a la vez o repetir los casos. Revisar el código previo a la ejecución para decidir estos detalles ***Depende de la versión, la parte de ejecución, p.ej en Kyber en C#, sería en esta parte: 
        
        KyberKeyGenerationParameters keyGenParameters = size switch
            {
                "kyber512" => new KyberKeyGenerationParameters(random, KyberParameters.kyber512),
                "kyber768" => new KyberKeyGenerationParameters(random, KyberParameters.kyber768),
                "kyber1024" => new KyberKeyGenerationParameters(random, KyberParameters.kyber1024),
                _ => throw new ArgumentException("Invalid size"),
            }; donde se puede modificar la ejecución.)

*** Para los casos en Java, se generan 2 archivos, uno global (.csv) que muestra los resultados finales, y 
otro con la información de la iteraciones para generar las gráficas, que sale con todas las iteraciones,
y subdividimos de forma manual en nuevos archivos según la versión del algoritmo, para poder obtener las gráficas correctamente. 

**Para ejecutar java, p.ej en Diltihium 1º javac -cp "lib/*:bin" -d bin src/Dilithium_Rend.java
2º java -cp "bin:lib/*" src.Dilithium_Rend

**En C#, limpiar con dotnet clean. Compilar con dotnet build, y ejecutar con dotnet run.
