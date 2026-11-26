import csv
import math
from pathlib import Path
from typing import Any

from paqueteria.excepciones.errores import ArchivoInvalidoError
from paqueteria.modelos.envio import (
    Sobre,
    Paquete,
    PaqueteFragil,
    PaqueteRefrigerado,
)
from paqueteria.servicios.cotizador import Cotizador


class ImportadorCSV:
    """Importa envíos empresariales y reporta las filas rechazadas."""

    CAMPOS_REQUERIDOS = (
        "tipo_envio",
        "remitente",
        "destinatario",
        "codigo_postal",
        "tipo_servicio",
    )

    TIPOS = {
        "sobre": Sobre,
        "paquete": Paquete,
        "paquetefragil": PaqueteFragil,
        "paqueterefrigerado": PaqueteRefrigerado,
    }

    def __init__(
        self,
        archivo_entrada: str | Path,
        cotizador: Cotizador | None = None,
    ) -> None:
        self.archivo_entrada = Path(archivo_entrada)
        self.cotizador = cotizador or Cotizador()
        self.errores: list[dict[str, Any]] = []
        self.envios_importados: list[Any] = []

    @staticmethod
    def _numero(valor: str, campo: str, permitir_cero: bool = False) -> float:
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError(f"{campo} debe ser numérico.")

        if not math.isfinite(numero):
            raise ValueError(f"{campo} debe ser un número finito.")

        if permitir_cero:
            if numero < 0:
                raise ValueError(f"{campo} no puede ser negativo.")
        elif numero <= 0:
            raise ValueError(f"{campo} debe ser mayor que cero.")

        return numero

    def leer_archivo(self) -> list[dict[str, str]]:
        if not self.archivo_entrada.is_file():
            raise ArchivoInvalidoError(
                f"No se encontró el archivo CSV '{self.archivo_entrada}'."
            )

        try:
            with self.archivo_entrada.open(
                "r", encoding="utf-8-sig", newline=""
            ) as archivo:
                lector = csv.DictReader(archivo)

                if not lector.fieldnames:
                    raise ArchivoInvalidoError(
                        "El CSV está vacío o no tiene encabezados."
                    )

                filas = []

                for fila in lector:
                    limpia = {
                        (clave.strip().lower() if clave else ""):
                        (valor.strip() if valor else "")
                        for clave, valor in fila.items()
                    }

                    if any(limpia.values()):
                        filas.append(limpia)

                return filas

        except ArchivoInvalidoError:
            raise
        except (csv.Error, UnicodeDecodeError, OSError) as exc:
            raise ArchivoInvalidoError(
                f"No se pudo leer el CSV: {exc}"
            ) from exc

    def validar_fila(self, fila: dict[str, str]):
        for campo in self.CAMPOS_REQUERIDOS:
            if not fila.get(campo):
                return False, f"Falta el campo '{campo}'.", None

        tipo = fila["tipo_envio"].strip().lower().replace("_", "")
        if tipo not in self.TIPOS:
            return False, f"Tipo de envío inválido: '{tipo}'.", None

        cp = fila["codigo_postal"].strip()
        if len(cp) != 5 or not cp.isdigit():
            return False, f"Código postal inválido: '{cp}'.", None

        servicio_original = fila["tipo_servicio"].strip().lower()
        servicios = {
            "estandar": "estandar",
            "estándar": "estandar",
            "expres": "express",
            "exprés": "express",
            "express": "express",
        }

        if servicio_original not in servicios:
            return False, "Tipo de servicio inválido.", None

        servicio = servicios[servicio_original]

        try:
            zona = self.cotizador.obtener_zona(cp)

            datos = {
                "numero_guia": fila.get("numero_guia", "").strip(),
                "remitente": fila["remitente"].strip(),
                "destinatario": fila["destinatario"].strip(),
                "codigo_postal": cp,
                "zona": zona,
                "tipo_servicio": servicio,
                "estado": (fila.get("estado") or "registrado").strip().lower(),
            }

            if not datos["numero_guia"]:
                return False, "Falta el número de guía.", None

            if tipo == "sobre":
                envio = Sobre(**datos)

            else:
                peso = self._numero(fila.get("peso", ""), "Peso")

                dimensiones = {
                    nombre: self._numero(fila.get(nombre, ""), nombre)
                    for nombre in ("largo", "ancho", "alto")
                }

                argumentos = {
                    **datos,
                    "peso": peso,
                    **dimensiones,
                }

                if tipo == "paquetefragil":
                    valor = self._numero(
                        fila.get("valor_declarado", ""),
                        "Valor declarado",
                    )
                    envio = PaqueteFragil(
                        **argumentos,
                        valor_declarado=valor,
                    )

                elif tipo == "paqueterefrigerado":
                    envio = PaqueteRefrigerado(**argumentos)

                else:
                    envio = Paquete(**argumentos)

            envio.calcular_costo(self.cotizador.tarifas)

            return True, "", envio

        except (ValueError, TypeError, KeyError) as exc:
            return False, str(exc), None

    def importar_envios(self, gestor_envios: Any = None) -> list[Any]:
        filas = self.leer_archivo()
        self.errores.clear()
        self.envios_importados.clear()

        for indice, fila in enumerate(filas, start=2):
            valido, motivo, envio = self.validar_fila(fila)

            if not valido:
                self.errores.append({
                    "fila": indice,
                    "motivo": motivo,
                    "datos": fila,
                })
                continue

            try:
                if gestor_envios is not None:
                    if not hasattr(gestor_envios, "registrar_envio"):
                        raise ValueError(
                            "El gestor no tiene registrar_envio()."
                        )
                    gestor_envios.registrar_envio(envio)

                self.envios_importados.append(envio)

            except (ValueError, TypeError) as exc:
                self.errores.append({
                    "fila": indice,
                    "motivo": str(exc),
                    "datos": fila,
                })

        return self.envios_importados

    def generar_reporte_errores(self) -> str:
        if not self.errores:
            return "Sin errores: todas las filas fueron válidas."

        lineas = [
            f"Reporte de filas rechazadas ({len(self.errores)}):"
        ]

        for error in self.errores:
            lineas.append(
                f"- Fila {error['fila']}: {error['motivo']}"
            )

        return "\n".join(lineas)