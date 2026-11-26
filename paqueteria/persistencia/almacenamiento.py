import json
from pathlib import Path

from paqueteria.excepciones.errores import ArchivoInvalidoError
from paqueteria.modelos.envio import (
    Envio,
    Sobre,
    Paquete,
    PaqueteFragil,
    PaqueteRefrigerado,
)
from paqueteria.modelos.repartidor import Vehiculo, Repartidor


class Almacenamiento:
    """Gestiona la persistencia JSON de envíos y repartidores."""

    TIPOS_ENVIO = {
        "Sobre": Sobre,
        "Paquete": Paquete,
        "PaqueteFragil": PaqueteFragil,
        "PaqueteRefrigerado": PaqueteRefrigerado,
    }

    def __init__(
        self,
        archivo_envios="datos/envios.json",
        archivo_repartidores="datos/repartidores.json",
        archivo_historiales="datos/historiales.json",
    ):
        self.archivo_envios = Path(archivo_envios)
        self.archivo_repartidores = Path(archivo_repartidores)
        self.archivo_historiales = Path(archivo_historiales)

    def _serializar_elemento(self, elemento):
        if isinstance(elemento, Envio):
            datos = elemento.__dict__.copy()
            datos["_tipo"] = type(elemento).__name__
            return datos

        if isinstance(elemento, Repartidor):
            return {
                "identificador": elemento.identificador,
                "nombre": elemento.nombre,
                "vehiculo": elemento.vehiculo.tipo,
                "envios_asignados": [
                    envio.numero_guia
                    for envio in elemento.envios_asignados
                ],
            }

        if hasattr(elemento, "to_dict") and callable(elemento.to_dict):
            return elemento.to_dict()

        if hasattr(elemento, "__dict__"):
            return elemento.__dict__.copy()

        return elemento

    def _guardar_json(self, ruta, datos):
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(datos, list):
                contenido = [
                    self._serializar_elemento(item)
                    for item in datos
                ]
            elif isinstance(datos, dict):
                contenido = {
                    clave: self._serializar_elemento(valor)
                    for clave, valor in datos.items()
                }
            else:
                contenido = self._serializar_elemento(datos)

            with ruta.open("w", encoding="utf-8") as archivo:
                json.dump(
                    contenido,
                    archivo,
                    ensure_ascii=False,
                    indent=2,
                )

        except (OSError, TypeError, ValueError) as exc:
            raise ArchivoInvalidoError(
                f"No se pudo escribir el archivo '{ruta}': {exc}"
            ) from exc

    def _cargar_json(self, ruta, defecto):
        if not ruta.exists():
            return defecto

        try:
            with ruta.open("r", encoding="utf-8") as archivo:
                return json.load(archivo)

        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ArchivoInvalidoError(
                f"El archivo JSON '{ruta}' está corrupto o mal formado."
            ) from exc

        except OSError as exc:
            raise ArchivoInvalidoError(
                f"No se pudo leer el archivo '{ruta}': {exc}"
            ) from exc

    def _reconstruir_envio(self, datos):
        tipo = datos.get("_tipo")

        if tipo not in self.TIPOS_ENVIO:
            raise ArchivoInvalidoError(
                f"Tipo de envío desconocido: {tipo}"
            )

        clase = self.TIPOS_ENVIO[tipo]

        campos = {
            "numero_guia": datos["numero_guia"],
            "destinatario": datos["destinatario"],
            "codigo_postal": datos["codigo_postal"],
            "zona": datos["zona"],
            "tipo_servicio": datos["tipo_servicio"],
            "estado": datos.get("estado", "registrado"),
            "remitente": datos.get("remitente", ""),
        }

        if clase is Sobre:
            campos["peso"] = datos.get(
                "peso_real",
                datos.get("peso"),
            )

        if issubclass(clase, Paquete):
            campos.update({
                "peso": datos["peso"],
                "largo": datos["largo"],
                "ancho": datos["ancho"],
                "alto": datos["alto"],
            })

        if issubclass(clase, PaqueteFragil):
            campos["valor_declarado"] = datos["valor_declarado"]

        envio = clase(**campos)
        envio.costo = datos.get("costo", 0.0)
        envio.intentos_fallidos = datos.get("intentos_fallidos", 0)

        return envio

    def guardar_envios(self, envios):
        self._guardar_json(self.archivo_envios, envios)

    def cargar_envios(self):
        datos = self._cargar_json(self.archivo_envios, [])

        return [
            self._reconstruir_envio(item)
            if isinstance(item, dict) and "_tipo" in item
            else item
            for item in datos
        ]

    def guardar_repartidores(self, repartidores):
        self._guardar_json(self.archivo_repartidores, repartidores)

    def cargar_repartidores(self):
        datos = self._cargar_json(self.archivo_repartidores, [])

        envios = {
            envio.numero_guia: envio
            for envio in self.cargar_envios()
        }

        repartidores = []

        for item in datos:
            vehiculo = Vehiculo(item["vehiculo"])

            repartidor = Repartidor(
                item["identificador"],
                item["nombre"],
                vehiculo,
            )

            for guia in item.get("envios_asignados", []):
                if guia in envios:
                    repartidor.envios_asignados.append(envios[guia])

            repartidores.append(repartidor)

        return repartidores

    def guardar_historiales(self, historiales):
        self._guardar_json(
            self.archivo_historiales,
            historiales,
        )

    def cargar_historiales(self):
        return self._cargar_json(
            self.archivo_historiales,
            {},
        )