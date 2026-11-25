
import random
import threading
import time


class Simulador:
    """Controla la simulación simultánea de las rutas de reparto."""

    def __init__(
        self,
        repartidores,
        duracion_jornada=60,
        tiempo_minimo=1,
        tiempo_maximo=3,
        generador=None
    ):
        """Inicializa el simulador y sus datos de trabajo."""
        if not isinstance(repartidores, (list, tuple)):
            raise ValueError("Los repartidores deben proporcionarse en una lista.")

        if not repartidores:
            raise ValueError("Debe existir al menos un repartidor.")

        if isinstance(duracion_jornada, bool) or not isinstance(
            duracion_jornada, (int, float)
        ) or duracion_jornada <= 0:
            raise ValueError("La duración de la jornada debe ser positiva.")

        if (
            isinstance(tiempo_minimo, bool)
            or isinstance(tiempo_maximo, bool)
            or not isinstance(tiempo_minimo, (int, float))
            or not isinstance(tiempo_maximo, (int, float))
            or tiempo_minimo <= 0
            or tiempo_maximo < tiempo_minimo
        ):
            raise ValueError("El intervalo de tiempo de entrega no es válido.")

        for repartidor in repartidores:
            if not hasattr(repartidor, "envios_asignados"):
                raise ValueError("Se recibió un repartidor no válido.")

        self.repartidores = list(repartidores)
        self.duracion_jornada = duracion_jornada
        self.tiempo_minimo = tiempo_minimo
        self.tiempo_maximo = tiempo_maximo

        self.progreso = {}
        self.resultados = []
        self.intentos_fallidos = {}

        self._generador = generador if generador is not None else random.Random()
        self._lock = threading.RLock()
        self._detener = threading.Event()
        self._iniciada = False
        self._finalizada = False
        self._inicio = None

        for repartidor in self.repartidores:
            identificador = repartidor.identificador
            if identificador in self.progreso:
                raise ValueError("Los repartidores deben tener identificadores únicos.")

            total = len(repartidor.consultar_envios())
            self.progreso[identificador] = {
                "nombre": repartidor.nombre,
                "total": total,
                "completados": 0,
                "exitosos": 0,
                "fallidos": 0,
                "porcentaje": 0,
                "estado": "Pendiente"
            }

    def _cambiar_estado(self, envio, nuevo_estado):
        """Actualiza el estado del envío utilizando su método, si existe."""
        metodo = getattr(envio, "cambiar_estado", None)

        if callable(metodo):
            metodo(nuevo_estado)
        else:
            envio.estado = nuevo_estado

    def _clave_envio(self, envio):
        """Obtiene una clave para identificar los intentos de cada envío."""
        guia = getattr(envio, "numero_guia", None)

        if guia is not None:
            return str(guia)

        return str(id(envio))

    def registrar_resultado(self, repartidor, envio, resultado, intento):
        """Registra el resultado de un intento de entrega."""
        registro = {
            "repartidor": repartidor.identificador,
            "nombre_repartidor": repartidor.nombre,
            "guia": getattr(envio, "numero_guia", "Sin guía"),
            "intento": intento,
            "resultado": resultado,
            "fecha_hora": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        with self._lock:
            self.resultados.append(registro)

            identificador = repartidor.identificador
            if resultado == "exitoso":
                self.progreso[identificador]["exitosos"] += 1
            else:
                self.progreso[identificador]["fallidos"] += 1

    def simular_entrega(self, repartidor, envio):
        """Simula un intento de entrega con un 10 % de probabilidad de fallo."""
        if repartidor not in self.repartidores:
            raise ValueError("El repartidor no pertenece a este simulador.")

        if envio not in repartidor.consultar_envios():
            raise ValueError("El envío no está asignado a este repartidor.")

        clave = self._clave_envio(envio)

        with self._lock:
            intento = self.intentos_fallidos.get(clave, 0) + 1

        self._cambiar_estado(envio, "en ruta")

        exito = self._generador.random() >= 0.10

        if exito:
            self._cambiar_estado(envio, "entregado")
            self.registrar_resultado(
                repartidor, envio, "exitoso", intento
            )
            return True

        with self._lock:
            self.intentos_fallidos[clave] = intento

        if intento >= 3:
            self._cambiar_estado(envio, "devuelto al remitente")
            resultado = "devuelto al remitente"
        else:
            self._cambiar_estado(envio, "en almacen")
            resultado = "fallido"

        self.registrar_resultado(
            repartidor, envio, resultado, intento
        )

        return False

    def _trabajar_repartidor(self, repartidor):
        """Ejecuta la ruta de un repartidor dentro de un hilo independiente."""
        identificador = repartidor.identificador
        envios = repartidor.consultar_envios()

        with self._lock:
            self.progreso[identificador]["estado"] = "En ruta"

        for envio in envios:
            if self._detener.is_set():
                break

            clave = self._clave_envio(envio)

            # Cada envío puede tener hasta tres intentos fallidos.
            with self._lock:
                intentos_previos = self.intentos_fallidos.get(clave, 0)

            if intentos_previos >= 3:
                continue

            while not self._detener.is_set():
                restante = self.duracion_jornada - (
                    time.monotonic() - self._inicio
                )

                if restante <= 0:
                    self._detener.set()
                    break

                duracion = self._generador.uniform(
                    self.tiempo_minimo,
                    self.tiempo_maximo
                )

                if duracion > restante:
                    time.sleep(restante)
                    self._detener.set()
                    break

                time.sleep(duracion)

                if self._detener.is_set():
                    break

                resultado = self.simular_entrega(repartidor, envio)

                with self._lock:
                    datos = self.progreso[identificador]

                    clave = self._clave_envio(envio)
                    intentos = self.intentos_fallidos.get(clave, 0)

                    if resultado or intentos >= 3:
                        datos["completados"] += 1

                    datos["porcentaje"] = (
                        datos["completados"] / datos["total"] * 100
                        if datos["total"] > 0 else 100
                )

                self.mostrar_progreso()

                if resultado:
                    break

                with self._lock:
                    intentos = self.intentos_fallidos.get(clave, 0)

                if intentos >= 3:
                    break

        with self._lock:
            self.progreso[identificador]["estado"] = "Jornada finalizada"

    def iniciar_simulacion(self):
        """Inicia simultáneamente las rutas de todos los repartidores."""
        if self._iniciada:
            raise RuntimeError("La simulación ya fue iniciada.")

        self._iniciada = True
        self._inicio = time.monotonic()

        hilos = []

        for repartidor in self.repartidores:
            hilo = threading.Thread(
                target=self._trabajar_repartidor,
                args=(repartidor,),
                name=f"Ruta-{repartidor.identificador}"
            )
            hilos.append(hilo)

        # Todos los hilos comienzan antes de esperar a que terminen.
        for hilo in hilos:
            hilo.start()

        for hilo in hilos:
            hilo.join()

        self._finalizada = True
        self.mostrar_progreso()

        return self.resultados.copy()

    def mostrar_progreso(self):
        """Muestra el avance actual de todos los repartidores."""
        with self._lock:
            print("\n========== AVANCE DE REPARTO ==========")

            for identificador, datos in self.progreso.items():
                print(
                    f"Repartidor: {datos['nombre']} "
                    f"({identificador})"
                )
                print(
                    f"Entregas procesadas: {datos['completados']}"
                    f"/{datos['total']}"
                )
                print(
                    f"Entregas exitosas: {datos['exitosos']}"
                )
                print(
                    f"Intentos fallidos: {datos['fallidos']}"
                )
                print(
                    f"Progreso: {datos['porcentaje']:.1f}%"
                )
                print(f"Estado: {datos['estado']}")
                print("---------------------------------------")

            print("=======================================\n")
