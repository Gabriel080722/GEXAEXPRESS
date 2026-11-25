from datetime import datetime
import json
from pathlib import Path
from typing import Any
from paqueteria.excepciones.errores import ArchivoInvalidoError


class Reportes:
    """Genera y guarda reportes operativos y financieros del sistema GexaExpress."""

    def __init__(self, archivo_salida: str | Path = "datos/reporte_diario.json") -> None:
        self.archivo_salida = Path(archivo_salida)
        self.ultimo_reporte: dict[str, Any] = {}

    def _obtener_campo(self, elemento: Any, clave: str, defecto: Any = None) -> Any:
        if isinstance(elemento, dict):
            return elemento.get(clave, defecto)
        return getattr(elemento, clave, defecto)

    def _inferir_tipo_envio(self, envio: Any) -> str:
        tipo = self._obtener_campo(envio, "tipo_envio")
        if tipo:
            return str(tipo).strip().lower()
        nombre_clase = type(envio).__name__.lower()
        if nombre_clase != "dict":
            return nombre_clase
        return "desconocido"

    def contar_envios_por_estado(self, envios: list[Any]) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for envio in envios:
            estado = str(self._obtener_campo(envio, "estado", "sin_estado")).strip().lower()
            conteo[estado] = conteo.get(estado, 0) + 1
        return conteo

    def calcular_ingresos(self, envios: list[Any]) -> dict[str, Any]:
        total = 0.0
        por_tipo_envio: dict[str, float] = {}
        por_tipo_servicio: dict[str, float] = {}

        for envio in envios:
            estado = str(self._obtener_campo(envio, "estado", "")).strip().lower()
            if estado == "cancelado":
                continue

            try:
                costo = float(self._obtener_campo(envio, "costo", 0.0) or 0.0)
            except (TypeError, ValueError):
                costo = 0.0

            tipo_envio = self._inferir_tipo_envio(envio)
            servicio = str(self._obtener_campo(envio, "tipo_servicio", "desconocido")).strip().lower()

            total += costo
            por_tipo_envio[tipo_envio] = round(por_tipo_envio.get(tipo_envio, 0.0) + costo, 2)
            por_tipo_servicio[servicio] = round(por_tipo_servicio.get(servicio, 0.0) + costo, 2)

        return {
            "total": round(total, 2),
            "por_tipo_envio": por_tipo_envio,
            "por_tipo_servicio": por_tipo_servicio,
        }

    def contar_entregas_por_repartidor(self, repartidores: list[Any]) -> dict[str, int]:
        entregas: dict[str, int] = {}

        for repartidor in repartidores:
            identificador = str(
                self._obtener_campo(
                    repartidor,
                    "identificador",
                    self._obtener_campo(repartidor, "id", self._obtener_campo(repartidor, "nombre", "sin_id")),
                )
            )
            asignados = self._obtener_campo(repartidor, "envios_asignados", []) or []
            completados = 0
            for envio in asignados:
                estado = str(self._obtener_campo(envio, "estado", "")).strip().lower()
                if estado in {"entregado", "completado", "entregada"}:
                    completados += 1
            entregas[identificador] = completados

        return entregas

    def generar_reporte_diario(
        self,
        envios: list[Any],
        repartidores: list[Any],
    ) -> dict[str, Any]:
        reporte = {
            "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
            "total_envios": len(envios),
            "total_repartidores": len(repartidores),
            "envios_por_estado": self.contar_envios_por_estado(envios),
            "ingresos": self.calcular_ingresos(envios),
            "entregas_por_repartidor": self.contar_entregas_por_repartidor(repartidores),
        }
        self.ultimo_reporte = reporte
        return reporte

    def guardar_reporte(self, reporte: dict[str, Any] | None = None) -> Path:
        datos = reporte if reporte is not None else self.ultimo_reporte
        if not datos:
            raise ArchivoInvalidoError("No hay ningún reporte generado para guardar.")

        try:
            self.archivo_salida.parent.mkdir(parents=True, exist_ok=True)
            with self.archivo_salida.open("w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            return self.archivo_salida
        except OSError as exc:
            raise ArchivoInvalidoError(
                f"No se pudo guardar el reporte en '{self.archivo_salida}': {exc}"
            ) from exc
