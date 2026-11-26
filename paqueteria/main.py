from paqueteria.persistencia.almacenamiento import Almacenamiento
from paqueteria.modelos.historial import Historial
from paqueteria.modelos.envio import (
    Sobre,
    Paquete,
    PaqueteFragil,
    PaqueteRefrigerado,
)
from paqueteria.modelos.repartidor import Repartidor, Vehiculo
from paqueteria.servicios.cotizador import Cotizador
from paqueteria.servicios.gestor_envios import GestorEnvios
from paqueteria.servicios.importador_csv import ImportadorCSV
from paqueteria.servicios.reportes import Reportes
from paqueteria.servicios.simulador import Simulador
from paqueteria.excepciones.errores import GexaExpressError


def cargar_sistema():
    """Carga los datos guardados e inicializa los servicios."""

    almacenamiento = Almacenamiento()
    cotizador = Cotizador()

    gestor = GestorEnvios(
        cotizador=cotizador,
        almacenamiento=almacenamiento
    )

    envios = almacenamiento.cargar_envios()
    repartidores = almacenamiento.cargar_repartidores()
    historiales = almacenamiento.cargar_historiales()

    gestor.envios = {
        envio.numero_guia: envio
        for envio in envios
    }

    for repartidor in repartidores:
        repartidor.envios_asignados = [
            gestor.envios[envio.numero_guia]
            for envio in repartidor.envios_asignados
            if envio.numero_guia in gestor.envios
        ]

    for guia, movimientos in historiales.items():
        historial = Historial(guia)
        historial.movimientos = movimientos
        gestor.historiales[guia] = historial

    for envio in envios:
        if envio.numero_guia not in gestor.historiales:
            historial = Historial(envio.numero_guia)
            historial.registrar_movimiento(envio.estado)
            gestor.historiales[envio.numero_guia] = historial

    return almacenamiento, gestor, repartidores


def mostrar_envios(gestor):
    """Muestra todos los envíos registrados."""

    if not gestor.envios:
        print("\nNo hay envíos registrados.")
        return

    print("\n========== ENVÍOS REGISTRADOS ==========")

    for envio in gestor.envios.values():
        print(
            f"Guía: {envio.numero_guia} | "
            f"Destinatario: {envio.destinatario} | "
            f"Estado: {envio.estado} | "
            f"Costo: ${envio.costo:.2f}"
        )


def registrar_envio_manual(gestor):
    """Registra manualmente un envío."""

    print("\n========== REGISTRAR ENVÍO ==========")
    print("1. Sobre")
    print("2. Paquete")
    print("3. Paquete frágil")
    print("4. Paquete refrigerado")

    try:
        opcion = input("\nTipo de envío: ").strip()

        if opcion not in ("1", "2", "3", "4"):
            print("Tipo de envío no válido.")
            return

        guia = input("Número de guía: ").strip()
        remitente = input("Remitente: ").strip()
        destinatario = input("Destinatario: ").strip()
        codigo_postal = input("Código postal: ").strip()
        servicio = input(
            "Servicio (estandar/express): "
        ).strip().lower()

        if opcion == "1":
            peso = float(input("Peso físico del sobre en kg: "))

            envio = Sobre(
                guia,
                destinatario,
                codigo_postal,
                None,
                servicio,
                remitente=remitente,
                peso=peso
            )

        else:
            peso = float(input("Peso en kg: "))
            largo = float(input("Largo en cm: "))
            ancho = float(input("Ancho en cm: "))
            alto = float(input("Alto en cm: "))

            if opcion == "2":
                envio = Paquete(
                    guia,
                    destinatario,
                    codigo_postal,
                    None,
                    servicio,
                    peso,
                    largo,
                    ancho,
                    alto,
                    remitente=remitente
                )

            elif opcion == "3":
                valor = float(input("Valor declarado: "))

                envio = PaqueteFragil(
                    guia,
                    destinatario,
                    codigo_postal,
                    None,
                    servicio,
                    peso,
                    largo,
                    ancho,
                    alto,
                    valor,
                    remitente=remitente
                )

            else:
                envio = PaqueteRefrigerado(
                    guia,
                    destinatario,
                    codigo_postal,
                    None,
                    servicio,
                    peso,
                    largo,
                    ancho,
                    alto,
                    remitente=remitente
                )

        envio = gestor.registrar_envio(envio)

        print("\nEnvío registrado correctamente.")
        print(f"Guía: {envio.numero_guia}")
        print(f"Zona: {envio.zona}")
        print(f"Costo: ${envio.costo:.2f}")

    except (ValueError, TypeError, GexaExpressError) as error:
        print(f"\nNo se pudo registrar el envío: {error}")


def importar_envios(gestor, cotizador):
    """Importa envíos empresariales desde un archivo CSV."""

    ruta = input("Ruta del archivo CSV: ").strip()

    try:
        importador = ImportadorCSV(ruta, cotizador)
        envios = importador.importar_envios(gestor)

        print(
            f"\nEnvíos importados correctamente: {len(envios)}"
        )
        print(importador.generar_reporte_errores())

    except (GexaExpressError, OSError, ValueError) as error:
        print(f"\nNo se pudo importar el archivo: {error}")


def ejecutar_simulacion(gestor, almacenamiento, repartidores):
    """Ejecuta la simulación de los repartidores."""

    if not repartidores:
        print("\nNo hay repartidores registrados.")
        return

    try:
        simulador = Simulador(
            repartidores=repartidores,
            gestor=gestor,
            almacenamiento=almacenamiento
        )

        resultados = simulador.iniciar_simulacion()

        print("\n========== RESULTADOS ==========")

        for resultado in resultados:
            print(resultado)

    except (ValueError, RuntimeError, GexaExpressError) as error:
        print(f"\nNo se pudo ejecutar la simulación: {error}")


def generar_reporte(gestor, repartidores):
    """Genera y guarda el reporte diario."""

    try:
        reportes = Reportes()

        reporte = reportes.generar_reporte_diario(
            list(gestor.envios.values()),
            repartidores
        )

        ruta = reportes.guardar_reporte(reporte)

        print("\n========== REPORTE DIARIO ==========")
        print(f"Total de envíos: {reporte['total_envios']}")
        print(
            f"Total de repartidores: "
            f"{reporte['total_repartidores']}"
        )
        print(f"Ingresos: ${reporte['ingresos']['total']:.2f}")
        print(f"Reporte guardado en: {ruta}")

    except (GexaExpressError, OSError, ValueError) as error:
        print(f"\nNo se pudo generar el reporte: {error}")


def consultar_historial(gestor):
    """Muestra el historial de un envío."""

    guia = input("\nNúmero de guía: ").strip()

    try:
        movimientos = gestor.consultar_historial(guia)

        print(f"\n========== HISTORIAL {guia} ==========")

        for movimiento in movimientos:
            print(
                f"Estado: {movimiento['estado']} | "
                f"Fecha: {movimiento['fecha_hora']}"
            )

    except GexaExpressError as error:
        print(f"\nNo se pudo consultar el historial: {error}")


def cambiar_estado_envio(gestor):
    """Permite cambiar el estado de un envío."""

    print("\n========== CAMBIAR ESTADO ==========")

    guia = input("Número de guía: ").strip()

    try:
        envio = gestor.consultar_envio(guia)

        print(f"Estado actual: {envio.estado}")
        print("\nEstados disponibles:")
        print("1. En almacén")
        print("2. En ruta")
        print("3. Entregado")
        print("4. Cancelado")
        print("5. Devuelto al remitente")

        opciones = {
            "1": "en almacen",
            "2": "en ruta",
            "3": "entregado",
            "4": "cancelado",
            "5": "devuelto al remitente"
        }

        opcion = input("\nNuevo estado: ").strip()

        if opcion not in opciones:
            print("Opción no válida.")
            return

        envio = gestor.cambiar_estado(
            guia,
            opciones[opcion]
        )

        print("\nEstado actualizado correctamente.")
        print(f"Guía: {envio.numero_guia}")
        print(f"Nuevo estado: {envio.estado}")

    except GexaExpressError as error:
        print(f"\nNo se pudo cambiar el estado: {error}")


def registrar_repartidor(gestor, repartidores):
    """Registra un nuevo repartidor."""

    print("\n========== REGISTRAR REPARTIDOR ==========")

    identificador = input("Identificador: ").strip()
    nombre = input("Nombre: ").strip()
    tipo = input(
        "Vehículo (motocicleta/camioneta): "
    ).strip().lower()

    try:
        vehiculo = Vehiculo(tipo)
        repartidor = Repartidor(
            identificador,
            nombre,
            vehiculo
        )

        gestor.registrar_repartidor(
            repartidor,
            repartidores
        )

        print("\nRepartidor registrado correctamente.")
        print(f"Identificador: {repartidor.identificador}")
        print(f"Nombre: {repartidor.nombre}")
        print(f"Vehículo: {repartidor.vehiculo.tipo}")
        print(
            f"Capacidad: "
            f"{repartidor.vehiculo.capacidad_maxima} kg"
        )

    except (GexaExpressError, ValueError) as error:
        print(f"\nNo se pudo registrar el repartidor: {error}")


def mostrar_repartidores(repartidores):
    """Muestra los repartidores registrados y su carga."""

    if not repartidores:
        print("\nNo hay repartidores registrados.")
        return

    print("\n========== REPARTIDORES ==========")

    for repartidor in repartidores:
        print(
            f"ID: {repartidor.identificador} | "
            f"Nombre: {repartidor.nombre} | "
            f"Vehículo: {repartidor.vehiculo.tipo} | "
            f"Carga: {repartidor.calcular_carga()} kg / "
            f"{repartidor.vehiculo.capacidad_maxima} kg | "
            f"Envíos: {len(repartidor.consultar_envios())}"
        )


def asignar_envio(gestor, repartidores):
    """Asigna un envío en almacén a un repartidor."""

    print("\n========== ASIGNAR ENVÍO ==========")

    if not repartidores:
        print("No hay repartidores registrados.")
        return

    guia = input("Número de guía: ").strip()

    try:
        envio = gestor.consultar_envio(guia)

        if isinstance(envio, Sobre) and envio.peso_real is None:
            peso = float(
                input("El sobre no tiene peso. Ingresa su peso físico en kg: ")
            )

            envio.establecer_peso_fisico(peso)

            gestor.almacenamiento.guardar_envios(
                list(gestor.envios.values())
            )

            print("Peso físico guardado correctamente.")

        mostrar_repartidores(repartidores)

        opcion = int(input("\nSelecciona el número de repartidor: "))

        if opcion < 1 or opcion > len(repartidores):
            print("Opción no válida.")
            return

        repartidor = repartidores[opcion - 1]

        envio = gestor.asignar_envio_repartidor(
            guia,
            repartidor,
            repartidores
        )

        print("\nEnvío asignado correctamente.")
        print(f"Guía: {envio.numero_guia}")
        print(f"Repartidor: {repartidor.nombre}")
        print(f"Carga actual: {repartidor.calcular_carga()} kg")

    except (GexaExpressError, ValueError, TypeError, OSError) as error:
        print(f"\nNo se pudo asignar el envío: {error}")


def main():
    """Inicia el sistema GexaExpress."""

    try:
        almacenamiento, gestor, repartidores = cargar_sistema()
        cotizador = gestor.cotizador

        print("================================")
        print("       SISTEMA GEXAEXPRESS")
        print("================================")

        while True:
            print("\n1. Consultar envíos")
            print("2. Registrar envío manualmente")
            print("3. Importar envíos CSV")
            print("4. Ejecutar simulación")
            print("5. Generar reporte diario")
            print("6. Consultar historial")
            print("7. Cambiar estado de envío")
            print("8. Registrar repartidor")
            print("9. Consultar repartidores")
            print("10. Asignar envío a repartidor")
            print("11. Salir")

            opcion = input("\nSelecciona una opción: ").strip()

            if opcion == "1":
                mostrar_envios(gestor)

            elif opcion == "2":
                registrar_envio_manual(gestor)

            elif opcion == "3":
                importar_envios(gestor, cotizador)

            elif opcion == "4":
                ejecutar_simulacion(
                    gestor,
                    almacenamiento,
                    repartidores
                )

            elif opcion == "5":
                generar_reporte(gestor, repartidores)

            elif opcion == "6":
                consultar_historial(gestor)

            elif opcion == "7":
                cambiar_estado_envio(gestor)

            elif opcion == "8":
                registrar_repartidor(gestor, repartidores)

            elif opcion == "9":
                mostrar_repartidores(repartidores)

            elif opcion == "10":
                asignar_envio(gestor, repartidores)

            elif opcion == "11":
                print("\nGracias por utilizar GexaExpress.")
                break

            else:
                print("\nOpción no válida. Intenta nuevamente.")

    except (GexaExpressError, OSError, ValueError) as error:
        print(f"\nError al iniciar GexaExpress: {error}")


if __name__ == "__main__":
    main()