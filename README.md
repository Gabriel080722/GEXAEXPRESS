GexaExpress

Descripción

GexaExpress es un sistema de gestión de paquetería desarrollado en Python mediante programación orientada a objetos. Permite registrar, cotizar, consultar y administrar envíos, asignarlos a repartidores y simular sus entregas.

El sistema administra sobres, paquetes, paquetes frágiles y paquetes refrigerados. También controla los estados y el historial de cada envío, además de conservar la información entre ejecuciones.

Integrantes

- Cruz Mogoyan Gabriel
- Ledo Martínez Alexa Ximena
- Manzano Saavedra Andrea Sai
- Barajas Calderón Erandi

Funcionalidades principales

- Registro y cotización de envíos.
- Cálculo de peso volumétrico para paquetes.
- Aplicación de cargos adicionales para paquetes frágiles y servicios exprés.
- Validación de las condiciones de los envíos refrigerados.
- Generación de números de guía únicos.
- Consulta del estado e historial de los envíos.
- Control de cambios de estado y cancelaciones.
- Registro y consulta de repartidores.
- Asignación de envíos según la capacidad del vehículo.
- Importación de envíos mediante archivos CSV.
- Identificación y reporte de registros inválidos durante la importación.
- Generación de reportes diarios.
- Simulación de jornadas laborales con varios repartidores.
- Almacenamiento de información mediante archivos JSON.

Tecnologías utilizadas

- Python 3.12.10.
- Programación orientada a objetos.
- Archivos CSV y JSON.
- "unittest" para las pruebas unitarias.
- "pytest" para ejecutar la suite de pruebas.
- Bibliotecas estándar de Python.

Requisitos

- Python 3.12.10.
- Git.
- pip.

Instalación

Clonar el repositorio:

git clone https://github.com/Gabriel080722/GEXAEXPRESS.git

Entrar a la carpeta:

cd GEXAEXPRESS

Crear un entorno virtual:

python -m venv .venv

Activarlo en Windows PowerShell:

.venv\Scripts\Activate.ps1

Instalar las dependencias:

pip install -r requirements.txt

Ejecución del programa

Desde la carpeta principal del proyecto, ejecutar:

python -m paqueteria.main

El programa muestra un menú con las siguientes opciones:

1. Consultar envíos.
2. Registrar envío manualmente.
3. Importar envíos CSV.
4. Ejecutar simulación.
5. Generar reporte diario.
6. Consultar historial.
7. Cambiar estado de envío.
8. Registrar repartidor.
9. Consultar repartidores.
10. Asignar envío a repartidor.
11. Salir.

Ejemplos de uso

Las siguientes indicaciones permiten probar las principales funcionalidades desde el menú del programa.

Registrar y cotizar un envío

1. Seleccionar la opción 2, registrar envío manualmente.
2. Introducir los datos solicitados por el programa.
3. Seleccionar el tipo de envío y servicio correspondiente.
4. Completar la información requerida.
5. Confirmar el registro y consultar la guía generada.

El sistema valida los datos y calcula el costo correspondiente al envío.

Consultar un envío e historial

1. Seleccionar la opción 1 para consultar envíos.
2. Buscar el envío mediante su número de guía.
3. Seleccionar la opción 6 para consultar su historial.
4. Verificar los movimientos registrados y sus fechas.

Cambiar el estado de un envío

1. Seleccionar la opción 7.
2. Introducir la guía del envío.
3. Indicar el nuevo estado solicitado por el programa.
4. Comprobar que el cambio se registre correctamente.

El sistema rechaza los cambios que no cumplen las transiciones permitidas.

Registrar y asignar un repartidor

1. Seleccionar la opción 8 para registrar un repartidor.
2. Introducir sus datos y el tipo de vehículo.
3. Seleccionar la opción 9 para consultar los repartidores registrados.
4. Seleccionar la opción 10 para asignar un envío.
5. Introducir los identificadores solicitados y comprobar el resultado.

El sistema verifica que el envío se encuentre disponible y que no se exceda la capacidad del vehículo.

Importar envíos mediante CSV

1. Seleccionar la opción 3.
2. Indicar la ruta del archivo CSV que se desea importar.
3. Para probar registros válidos, utilizar "datos/envios_empresariales_ok.csv".
4. Para comprobar los rechazos, utilizar "datos/envios_empresariales_errores.csv".
5. Revisar cuántos registros fueron aceptados y cuáles fueron rechazados, junto con sus motivos.

Ejecutar una simulación

1. Registrar repartidores y asignarles envíos disponibles.
2. Seleccionar la opción 4.
3. Iniciar la simulación de la jornada.
4. Observar el progreso de los repartidores y los resultados de las entregas.

La simulación permite ejecutar las jornadas de varios repartidores simultáneamente y contempla intentos de entrega fallidos.

Generar un reporte diario

1. Seleccionar la opción 5.
2. Ejecutar la generación del reporte.
3. Revisar el archivo generado con los envíos agrupados por estado, los ingresos y las entregas realizadas por repartidor.

Pruebas

Para ejecutar todas las pruebas:

python -m pytest -v

Las pruebas verifican el funcionamiento de los modelos, el cotizador, los repartidores y el simulador, incluyendo validaciones, errores y casos de rechazo.

Datos de ejemplo

La carpeta "datos/" contiene archivos de ejemplo para probar las funcionalidades:

- "tarifas_zonas.csv": tarifas y zonas utilizadas para calcular cotizaciones.
- "envios_empresariales_ok.csv": registros empresariales válidos.
- "envios_empresariales_errores.csv": registros con datos inválidos para comprobar su rechazo.

El sistema utiliza también archivos JSON para conservar los envíos, repartidores e historiales. Estos archivos se generan o actualizan durante el funcionamiento del programa.

Para probar la importación, se puede seleccionar la opción 3 del menú e indicar el archivo CSV correspondiente. El sistema registra las filas válidas y reporta las que no cumplen las validaciones.

Estructura del proyecto

GEXAEXPRESS/
│
├── datos/
│   ├── envios_empresariales_errores.csv
│   ├── envios_empresariales_ok.csv
│   └── tarifas_zonas.csv
│
├── docs/
│   └── diseno.md
│
├── paqueteria/
│   ├── excepciones/
│   │   └── errores.py
│   ├── modelos/
│   │   ├── envio.py
│   │   ├── historial.py
│   │   └── repartidor.py
│   ├── persistencia/
│   │   └── almacenamiento.py
│   ├── servicios/
│   │   ├── cotizador.py
│   │   ├── gestor_envios.py
│   │   ├── importador_csv.py
│   │   ├── reportes.py
│   │   └── simulador.py
│   └── main.py
│
├── tests/
│   ├── test_basico.py
│   ├── test_cotizador.py
│   ├── test_envio.py
│   ├── test_repartidor.py
│   └── test_simulador.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── probar_parte3.py

Organización de los módulos

- modelos: contiene las clases que representan los envíos, el historial y los repartidores.
- servicios: contiene la lógica para cotizar, administrar, importar, generar reportes y simular entregas.
- persistencia: administra la lectura y escritura de los archivos JSON.
- excepciones: define los errores personalizados del sistema.
- tests: contiene las pruebas automatizadas.

Persistencia de datos

El sistema utiliza archivos JSON para conservar los envíos, repartidores e historiales, permitiendo recuperar la información después de cerrar y volver a ejecutar el programa.

Los archivos CSV se utilizan para importar envíos empresariales y consultar las tarifas por zona.

Documentación del diseño

El diseño del sistema, sus clases, relaciones, responsabilidades y decisiones de implementación se describen en "docs/diseno.md".

Proyecto académico

Proyecto desarrollado como parte de la asignatura de Programación Orientada a Objetos.