import json
from pathlib import Path
from typing import Any
from paqueteria.excepciones.errores import ArchivoInvalidoError


class Almacenamiento:
    """Gestiona la persistencia en JSON de envíos, repartidores e historiales."""

    def __init__(
        self,
        archivo_envios: str | Path = "datos/envios.json",
        archivo_repartidores: str | Path = "datos/repartidores.json",
        archivo_historiales: str | Path = "datos/historiales.json",
    ) -> None:
        self.archivo_envios = Path(archivo_envios)
        self.archivo_repartidores = Path(archivo_repartidores)
        self.archivo_historiales = Path(archivo_historiales)

    def _serializar_elemento(self, elemento: Any) -> Any:
        if hasattr(elemento, "to_dict") and callable(elemento.to_dict):
            return elemento.to_dict()
        if hasattr(elemento, "__dict__"):
            return elemento.__dict__
        return elemento

    def _guardar_json(self, ruta: Path, datos: list[Any] | dict[str, Any]) -> None:
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(datos, list):
                contenido = [self._serializar_elemento(item) for item in datos]
            elif isinstance(datos, dict):
                contenido = {
                    clave: self._serializar_elemento(valor)
                    for clave, valor in datos.items()
                }
            else:
                contenido = self._serializar_elemento(datos)

            with ruta.open("w", encoding="utf-8") as archivo:
                json.dump(contenido, archivo, ensure_ascii=False, indent=2)
        except OSError as exc:
            raise ArchivoInvalidoError(f"No se pudo escribir el archivo '{ruta}': {exc}") from exc

    def _cargar_json(self, ruta: Path, defecto: Any) -> Any:
        if not ruta.exists():
            return defecto
        try:
            with ruta.open("r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError as exc:
            raise ArchivoInvalidoError(f"El archivo JSON '{ruta}' está corrupto o mal formado.") from exc
        except OSError as exc:
            raise ArchivoInvalidoError(f"No se pudo leer el archivo '{ruta}': {exc}") from exc

    def guardar_envios(self, envios: list[Any]) -> None:
        self._guardar_json(self.archivo_envios, envios)

    def cargar_envios(self) -> list[Any]:
        return self._cargar_json(self.archivo_envios, [])

    def guardar_repartidores(self, repartidores: list[Any]) -> None:
        self._guardar_json(self.archivo_repartidores, repartidores)

    def cargar_repartidores(self) -> list[Any]:
        return self._cargar_json(self.archivo_repartidores, [])

    def guardar_historiales(self, historiales: dict[str, Any] | list[Any]) -> None:
        self._guardar_json(self.archivo_historiales, historiales)

    def cargar_historiales(self) -> dict[str, Any] | list[Any]:
        return self._cargar_json(self.archivo_historiales, {})
