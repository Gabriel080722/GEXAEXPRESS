from datetime import datetime

from paqueteria.modelos.envio import Envio
from paqueteria.modelos.historial import Historial
from paqueteria.servicios.cotizador import Cotizador
from paqueteria.excepciones.errores import (
    EnvioInvalidoError,
    EstadoInvalidoError,
)


class GestorEnvios:
    """Administra los envíos, sus historiales y sus asignaciones."""

    TRANSICIONES = {
        "registrado": ("en almacen", "cancelado"),
        "en almacen": ("en ruta", "cancelado"),
        "en ruta": (
            "entregado",
            "en almacen",
            "devuelto al remitente",
        ),
        "entregado": (),
        "cancelado": (),
        "devuelto al remitente": (),
    }

    def __init__(self, cotizador=None, almacenamiento=None, reloj=None):
        self.cotizador = cotizador or Cotizador()
        self.almacenamiento = almacenamiento
        self.reloj = reloj or datetime.now

        self.envios = {}
        self.historiales = {}

    def _guardar_datos(self):
        """Guarda los envíos y sus historiales."""
        if self.almacenamiento is not None:
            self.almacenamiento.guardar_envios(
                list(self.envios.values())
            )

            datos_historiales = {
                guia: historial.obtener_historial()
                for guia, historial in self.historiales.items()
            }

            self.almacenamiento.guardar_historiales(
                datos_historiales
            )

    def registrar_envio(self, envio):
        """Registra un envío y calcula su costo."""

        if not isinstance(envio, Envio):
            raise EnvioInvalidoError(
                "Debe proporcionarse un objeto de envío válido."
            )

        guia = envio.numero_guia

        if guia in self.envios:
            raise EnvioInvalidoError(
                f"Ya existe un envío con la guía {guia}."
            )

        try:
            envio.costo = self.cotizador.calcular_cotizacion(envio)
        except (ValueError, TypeError) as error:
            raise EnvioInvalidoError(str(error)) from error

        self.envios[guia] = envio

        historial = Historial(guia)
        historial.registrar_movimiento(
            envio.estado,
            self.reloj()
        )

        self.historiales[guia] = historial
        self._guardar_datos()

        return envio

    def consultar_envio(self, numero_guia):
        """Busca un envío mediante su número de guía."""

        envio = self.envios.get(str(numero_guia).strip())

        if envio is None:
            raise EnvioInvalidoError(
                f"No se encontró el envío {numero_guia}."
            )

        return envio

    def cambiar_estado(
        self,
        numero_guia,
        nuevo_estado,
        fecha_hora=None
    ):
        """Cambia el estado y registra el movimiento."""

        envio = self.consultar_envio(numero_guia)

        if not isinstance(nuevo_estado, str):
            raise EstadoInvalidoError("El estado no es válido.")

        nuevo_estado = nuevo_estado.lower().strip()

        if nuevo_estado not in envio.ESTADOS_VALIDOS:
            raise EstadoInvalidoError(
                f"El estado '{nuevo_estado}' no es válido."
            )

        estados_permitidos = self.TRANSICIONES.get(envio.estado, ())

        if nuevo_estado not in estados_permitidos:
            raise EstadoInvalidoError(
                f"No se permite cambiar de '{envio.estado}' "
                f"a '{nuevo_estado}'."
            )

        if fecha_hora is None:
            fecha_hora = self.reloj()

        envio.estado = nuevo_estado

        self.historiales[envio.numero_guia].registrar_movimiento(
            nuevo_estado,
            fecha_hora
        )

        self._guardar_datos()
        return envio

    def registrar_intento_fallido(
        self,
        numero_guia,
        fecha_hora=None
    ):
        """Incrementa los intentos fallidos de un envío."""

        envio = self.consultar_envio(numero_guia)

        if envio.estado != "en ruta":
            raise EstadoInvalidoError(
                "El intento fallido debe registrarse durante una ruta."
            )

        envio.intentos_fallidos += 1

        self._guardar_datos()
        return envio.intentos_fallidos

    def registrar_repartidor(self, repartidor, repartidores):
        """Registra un repartidor y guarda la lista actualizada."""

        if any(
            existente.identificador == repartidor.identificador
            for existente in repartidores
        ):
            raise EnvioInvalidoError(
                "Ya existe un repartidor con ese identificador."
            )

        repartidores.append(repartidor)

        if self.almacenamiento is not None:
            self.almacenamiento.guardar_repartidores(repartidores)

        return repartidor

    def asignar_envio_repartidor(
        self,
        numero_guia,
        repartidor,
        repartidores
    ):
        """Asigna un envío en almacén a un repartidor."""

        envio = self.consultar_envio(numero_guia)

        if envio.estado != "en almacen":
            raise EstadoInvalidoError(
                "Solo se pueden asignar envíos que estén en almacén."
            )

        for otro in repartidores:
            if otro is repartidor:
                continue

            if any(
                asignado.numero_guia == envio.numero_guia
                for asignado in otro.consultar_envios()
            ):
                raise EnvioInvalidoError(
                    "El envío ya está asignado a otro repartidor."
                )

        try:
            repartidor.asignar_envio(envio)
        except ValueError as error:
            raise EnvioInvalidoError(str(error)) from error

        if self.almacenamiento is not None:
            self.almacenamiento.guardar_repartidores(repartidores)

        return envio

    def consultar_historial(self, numero_guia):
        """Devuelve los movimientos de un envío."""

        guia = str(numero_guia).strip()

        if guia not in self.historiales:
            raise EnvioInvalidoError(
                f"No existe historial para el envío {guia}."
            )

        return self.historiales[guia].obtener_historial()