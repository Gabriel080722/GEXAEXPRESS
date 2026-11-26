Diseño del sistema GexaExpress

1. Descripción general

GexaExpress es un sistema de gestión de paquetería desarrollado en Python utilizando el paradigma de programación orientada a objetos.

Su objetivo es administrar el registro, cotización, seguimiento y entrega de envíos. Para ello, el sistema organiza sus responsabilidades en modelos, servicios, persistencia y excepciones.

2. Organización del sistema

El proyecto se divide en los siguientes módulos:

- modelos: contiene las clases que representan los envíos, sus historiales y los repartidores.
- servicios: contiene la lógica para cotizar, gestionar, importar, reportar y simular las operaciones de paquetería.
- persistencia: administra el almacenamiento y recuperación de la información.
- excepciones: contiene las excepciones utilizadas para controlar errores específicos del sistema.
- main.py: funciona como punto de entrada y permite interactuar con el sistema mediante un menú.

3. Modelos principales

Envio

Es la clase base que representa un envío. Contiene la información general, como número de guía, remitente, destinatario, dirección, código postal, servicio, costo y estado.

También establece los comportamientos comunes de los diferentes tipos de envío.

Sobre

Representa los envíos de tipo sobre. Su costo se determina mediante una tarifa fija dependiendo de la zona de destino.

Paquete

Representa los envíos que se cobran de acuerdo con su peso facturable. Este se determina comparando el peso real con el peso volumétrico.

PaqueteFragil

Es una especialización de Paquete. Aplica un cargo adicional del 20 % y requiere un seguro equivalente al 3 % del valor declarado.

PaqueteRefrigerado

Es una especialización de Paquete que solamente permite el servicio exprés y destinos que no sean de zona nacional.

Historial

Registra los cambios de estado de cada envío junto con su fecha y hora, permitiendo consultar sus movimientos.

Vehiculo

Representa el vehículo utilizado por un repartidor. Define su capacidad máxima de carga.

Repartidor

Representa al personal encargado de realizar las entregas. Contiene sus datos, vehículo y envíos asignados. También permite calcular la carga que transporta.

4. Servicios del sistema

Cotizador

Calcula el costo de los envíos considerando su tipo, zona de destino, peso y servicio contratado.

Las tarifas por zona se obtienen del archivo "tarifas_zonas.csv".

GestorEnvios

Administra el registro de envíos, consulta de información, cambios de estado, historial, registro de repartidores y asignación de envíos.

También valida las transiciones permitidas entre los diferentes estados.

ImportadorCSV

Permite importar envíos empresariales desde archivos CSV. Procesa los registros, identifica los datos inválidos y genera un reporte de errores.

Reportes

Genera reportes diarios con la cantidad de envíos por estado, los ingresos por tipo de envío y servicio, y las entregas realizadas por cada repartidor.

Los reportes se pueden guardar en archivos JSON.

Simulador

Simula una jornada laboral en la que los repartidores realizan sus entregas de manera concurrente.

Cada entrega tiene una duración aleatoria y existe una probabilidad del 10 % de que el intento falle. Después de tres intentos fallidos, el envío se devuelve al remitente.

Durante la simulación se muestra el progreso de cada repartidor.

5. Persistencia de datos

La clase "Almacenamiento" se encarga de guardar y recuperar la información del sistema mediante archivos JSON.

Se conservan los siguientes datos:

- Envíos registrados.
- Repartidores y sus asignaciones.
- Historiales de los envíos.

Esto permite mantener la información disponible entre diferentes ejecuciones del programa.

6. Estados de los envíos

Los envíos pueden pasar por los siguientes estados:

- Registrado: el envío acaba de ser registrado.
- En almacén: el envío se encuentra disponible para su asignación.
- En ruta: el repartidor está realizando la entrega.
- Entregado: el envío llegó correctamente a su destinatario.
- Cancelado: el envío fue cancelado antes de salir a ruta.
- Devuelto al remitente: el envío alcanzó el límite de intentos fallidos.

Los cambios de estado son controlados por "GestorEnvios" para evitar transiciones no permitidas.

7. Relaciones entre las clases

El sistema utiliza herencia para representar los diferentes tipos de envío. "Sobre" y "Paquete" son especializaciones de "Envio", mientras que "PaqueteFragil" y "PaqueteRefrigerado" son especializaciones de "Paquete".

Un "Repartidor" tiene asociado un "Vehiculo" y puede tener varios envíos asignados.

Cada envío cuenta con un historial que registra sus movimientos.

Los servicios utilizan los modelos para realizar las operaciones correspondientes, mientras que "Almacenamiento" conserva la información.

8. Manejo de excepciones

El sistema utiliza excepciones personalizadas para controlar situaciones como envíos inválidos, cambios de estado no permitidos y errores relacionados con archivos.

Esto permite informar los problemas durante la ejecución y evitar operaciones incorrectas.

9. Pruebas

El proyecto cuenta con pruebas automatizadas para verificar el funcionamiento de los modelos, el cotizador, los repartidores y el simulador.

Las pruebas se ejecutan mediante:

python -m pytest -v

10. Contribuciones de los integrantes

El desarrollo del proyecto se dividió en cuatro áreas principales, procurando distribuir las responsabilidades de programación, lógica, validaciones y pruebas entre las integrantes del equipo.

Erandi Barajas Calderón: Desarrolló los tipos de envío y el cotizador. Su trabajo incluye las clases "Envio", "Sobre", "Paquete", "PaqueteFragil" y "PaqueteRefrigerado", así como los cálculos de peso, costos, recargos, seguros y validaciones de los envíos.

Alexa Ledo Martínez Ximena: Desarrolló las clases de repartidores y vehículos, además de la simulación de entregas. Su trabajo incluye el control de capacidades, la asignación de envíos y la ejecución simultánea de las jornadas de los repartidores.

Andrea Manzano Saavedra: Desarrolló la persistencia, la importación de archivos CSV y la generación de reportes. Su trabajo incluye el almacenamiento y recuperación de envíos, repartidores e historiales, así como la validación de registros empresariales y el cálculo de reportes diarios.

Gabriel Cruz Mogoyan: Desarrolló las excepciones personalizadas, la clase "Historial", el "GestorEnvios" y el menú principal. También se encargó de coordinar la integración de los módulos, implementar el seguimiento y los cambios de estado de los envíos, y realizar correcciones y pruebas generales para comprobar el funcionamiento del sistema.

Además, el equipo colaboró en la integración y revisión de la simulación para conectar correctamente las entregas con los estados, historiales y datos almacenados.

11. Decisiones de diseño

Concepto| Aplicación en GexaExpress| Justificación
Encapsulamiento| Se utilizan atributos y métodos para controlar el acceso y modificación de los datos de envíos y repartidores.| Permite proteger la información y mantener un control sobre las operaciones.
Herencia| Las clases "Sobre" y "Paquete" heredan de "Envio". A su vez, "PaqueteFragil" y "PaqueteRefrigerado" heredan de "Paquete".| Permite reutilizar características y agregar comportamientos específicos a cada tipo de envío.
Clases abstractas| "Envio" define una estructura común y establece el método abstracto "calcular_costo".| Evita crear envíos genéricos y obliga a cada tipo concreto a implementar su propio cálculo.
Polimorfismo| Los diferentes tipos de envío implementan su propio método "calcular_costo".| Permite calcular los costos sin necesitar condiciones distintas para cada clase.
Composición y asociación| Un "Repartidor" mantiene un vehículo y administra sus envíos asignados. Los servicios trabajan con los modelos del sistema.| Permite organizar las responsabilidades y relaciones entre los objetos.
Excepciones| Se utilizan excepciones personalizadas para errores de envíos, estados, capacidad y archivos.| Facilita identificar y controlar errores específicos.
Archivos| Se utilizan archivos JSON para conservar la información y CSV para importar datos y consultar tarifas.| Permite mantener los datos entre ejecuciones y procesar información externa.
Concurrencia| El simulador utiliza hilos para ejecutar las jornadas de varios repartidores simultáneamente.| Permite representar entregas concurrentes y mostrar el progreso de cada repartidor.

Alternativas de diseño consideradas

1. Almacenamiento de información

Se pudo utilizar una base de datos para conservar los envíos, repartidores e historiales. Sin embargo, se eligieron archivos JSON porque permiten almacenar y recuperar la información sin instalar herramientas adicionales, manteniendo una implementación sencilla.

2. Simulación de repartidores

Se pudo ejecutar la jornada de cada repartidor de manera secuencial. Se eligió utilizar hilos para permitir que varios repartidores realicen sus entregas al mismo tiempo, representando mejor el funcionamiento de una jornada de trabajo.

Uso de inteligencia artificial

Durante el desarrollo de GexaExpress se utilizó ChatGPT como herramienta de apoyo para comprender conceptos de programación, resolver dudas y buscar orientación ante algunos problemas que surgieron durante la implementación.

Algunos ejemplos de las consultas realizadas fueron:

- ¿Cómo podemos organizar las clases para que cada una tenga responsabilidades claras?
- ¿Qué aspectos debemos considerar para implementar correctamente la herencia y el polimorfismo?
- ¿Cómo podemos detectar por qué un método no está funcionando como esperamos?
- ¿Qué debemos tomar en cuenta para manejar errores al leer archivos JSON y CSV?
- ¿Cómo podemos comprobar que los hilos permiten ejecutar las entregas de varios repartidores al mismo tiempo?
- ¿Qué pruebas podríamos realizar para verificar que las validaciones funcionan correctamente?

Las respuestas se utilizaron como orientación para analizar distintas posibilidades y comprender mejor los problemas. El equipo revisó las sugerencias, realizó sus propias modificaciones y comprobó el funcionamiento mediante pruebas y ejecuciones del programa.

La inteligencia artificial fue una herramienta de consulta y aprendizaje durante el desarrollo, mientras que las decisiones de implementación, integración y verificación fueron responsabilidad del equipo.