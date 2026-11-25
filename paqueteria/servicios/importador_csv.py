import csv
from pathlib import Path
from typing import Any
from paqueteria.excepciones.errores import ArchivoInvalidoError


class ImportadorCSV:
    """Importa envíos empresariales desde un archivo CSV, valida filas y reporta errores."""

    CAMPOS_REQUERIDOS = (
        "tipo_envio",
        "remitente",
        "destinatario",
        "codigo_postal",
        "tipo_servicio",
    )
    TIPOS_ENVIO_VALIDOS = {"sobre", "paquete", "paquetefragil", "paqueterefrigerado"}
    SERVICIOS_VALIDOS = {"estandar", "estándar", "expres", "exprés", "express"}

    def __init__(self, archivo_entrada: str | Path) -> None:
        self.archivo_entrada = Path(archivo_entrada)
        self.errores: list[dict[str, Any]] = []
        self.envios_importados: list[dict[str, Any]] = []

    def leer_archivo(self) -> list[dict[str, str]]:
        if not self.archivo_entrada.exists() or not self.archivo_entrada.is_file():
            raise ArchivoInvalidoError(f"No se encontró el archivo CSV '{self.archivo_entrada}'.")

        try:
            with self.archivo_entrada.open("r", encoding="utf-8-sig", newline="") as archivo:
                lector = csv.DictReader(archivo)
                if not lector.fieldnames:
                    raise ArchivoInvalidoError("El archivo CSV está vacío o no tiene encabezados.")

                filas: list[dict[str, str]] = []
                for fila in lector:
                    fila_limpia = {
                        (clave.strip().lower() if clave else ""): (valor.strip() if valor else "")
                        for clave, valor in fila.items()
                    }
                    if any(valor != "" for valor in fila_limpia.values()):
                        filas.append(fila_limpia)
                return filas
        except ArchivoInvalidoError:
            raise
        except (csv.Error, UnicodeDecodeError, OSError) as exc:
            raise ArchivoInvalidoError(f"Error al leer el CSV '{self.archivo_entrada}': {exc}") from exc

    def validar_fila(self, fila: dict[str, str]) -> tuple[bool, str, dict[str, Any] | None]:
        for campo in self.CAMPOS_REQUERIDOS:
            if not fila.get(campo):
                return False, f"Falta el campo obligatorio '{campo}'.", None

        tipo_envio = fila["tipo_envio"].strip().lower()
        if tipo_envio not in self.TIPOS_ENVIO_VALIDOS:
            return False, f"Tipo de envío inválido '{fila['tipo_envio']}'.", None

        cp = fila["codigo_postal"].strip()
        if not cp.isdigit() or len(cp) != 5:
            return False, f"Código postal inválido '{cp}' (debe tener 5 dígitos).", None

        servicio = fila["tipo_servicio"].strip().lower()
        if servicio not in self.SERVICIOS_VALIDOS:
            return False, f"Tipo de servicio inválido '{fila['tipo_servicio']}'.", None

        datos_limpios: dict[str, Any] = {
            "tipo_envio": tipo_envio,
            "remitente": fila["remitente"].strip(),
            "destinatario": fila["destinatario"].strip(),
            "codigo_postal": cp,
            "tipo_servicio": servicio,
            "estado": (fila.get("estado") or "registrado").strip().lower(),
        }

        if tipo_envio != "sobre":
            try:
                peso = float(fila.get("peso", ""))
                if peso <= 0:
                    return False, "El peso debe ser mayor a 0.", None
                datos_limpios["peso"] = peso
            except ValueError:
                return False, f"Peso inválido '{fila.get('peso', '')}'.", None

            for dimension in ("largo", "ancho", "alto"):
                valor_dim = fila.get(dimension, "").strip()
                if valor_dim:
                    try:
                        dim_num = float(valor_dim)
                        if dim_num <= 0:
                            return False, f"La dimensión '{dimension}' debe ser mayor a 0.", None
                        datos_limpios[dimension] = dim_num
                    except ValueError:
                        return False, f"Dimensión '{dimension}' inválida '{valor_dim}'.", None

        if "costo" in fila and fila["costo"].strip():
            try:
                costo = float(fila["costo"].strip())
                if costo < 0:
                    return False, "El costo no puede ser negativo.", None
                datos_limpios["costo"] = costo
            except ValueError:
                return False, f"Costo inválido '{fila['costo']}'.", None
        else:
            datos_limpios["costo"] = 0.0

        return True, "", datos_limpios

    def importar_envios(self, gestor_envios: Any = None) -> list[dict[str, Any]]:
        filas = self.leer_archivo()
        self.errores.clear()
        self.envios_importados.clear()

        for indice, fila in enumerate(filas, start=2):
            es_valida, motivo, datos_limpios = self.validar_fila(fila)
            if not es_valida or datos_limpios is None:
                self.errores.append({
                    "fila": indice,
                    "motivo": motivo,
                    "datos": fila,
                })
                continue

            if gestor_envios is not None and hasattr(gestor_envios, "registrar_envio"):
                gestor_envios.registrar_envio(datos_limpios)

            self.envios_importados.append(datos_limpios)

        return self.envios_importados

    def generar_reporte_errores(self) -> str:
        if not self.errores:
            return "Sin errores: todas las filas del CSV fueron válidas."

        lineas = [f"Reporte de filas rechazadas ({len(self.errores)}):"]
        for err in self.errores:
            lineas.append(f"- Fila {err['fila']}: {err['motivo']}")
        return "\n".join(lineas)
import csv
from pathlib import Path
from typing import Any
from paqueteria.excepciones.errores import ArchivoInvalidoError


class ImportadorCSV:
    """Importa envíos empresariales desde un archivo CSV, valida filas y reporta errores."""

    CAMPOS_REQUERIDOS = (
        "tipo_envio",
        "remitente",
        "destinatario",
        "codigo_postal",
        "tipo_servicio",
    )
    TIPOS_ENVIO_VALIDOS = {"sobre", "paquete", "paquetefragil", "paqueterefrigerado"}
    SERVICIOS_VALIDOS = {"estandar", "estándar", "expres", "exprés", "express"}

    def __init__(self, archivo_entrada: str | Path) -> None:
        self.archivo_entrada = Path(archivo_entrada)
        self.errores: list[dict[str, Any]] = []
        self.envios_importados: list[dict[str, Any]] = []

    def leer_archivo(self) -> list[dict[str, str]]:
        if not self.archivo_entrada.exists() or not self.archivo_entrada.is_file():
            raise ArchivoInvalidoError(f"No se encontró el archivo CSV '{self.archivo_entrada}'.")

        try:
            with self.archivo_entrada.open("r", encoding="utf-8-sig", newline="") as archivo:
                lector = csv.DictReader(archivo)
                if not lector.fieldnames:
                    raise ArchivoInvalidoError("El archivo CSV está vacío o no tiene encabezados.")

                filas: list[dict[str, str]] = []
                for fila in lector:
                    fila_limpia = {
                        (clave.strip().lower() if clave else ""): (valor.strip() if valor else "")
                        for clave, valor in fila.items()
                    }
                    if any(valor != "" for valor in fila_limpia.values()):
                        filas.append(fila_limpia)
                return filas
        except ArchivoInvalidoError:
            raise
        except (csv.Error, UnicodeDecodeError, OSError) as exc:
            raise ArchivoInvalidoError(f"Error al leer el CSV '{self.archivo_entrada}': {exc}") from exc

    def validar_fila(self, fila: dict[str, str]) -> tuple[bool, str, dict[str, Any] | None]:
        for campo in self.CAMPOS_REQUERIDOS:
            if not fila.get(campo):
                return False, f"Falta el campo obligatorio '{campo}'.", None

        tipo_envio = fila["tipo_envio"].strip().lower()
        if tipo_envio not in self.TIPOS_ENVIO_VALIDOS:
            return False, f"Tipo de envío inválido '{fila['tipo_envio']}'.", None

        cp = fila["codigo_postal"].strip()
        if not cp.isdigit() or len(cp) != 5:
            return False, f"Código postal inválido '{cp}' (debe tener 5 dígitos).", None

        servicio = fila["tipo_servicio"].strip().lower()
        if servicio not in self.SERVICIOS_VALIDOS:
            return False, f"Tipo de servicio inválido '{fila['tipo_servicio']}'.", None

        datos_limpios: dict[str, Any] = {
            "tipo_envio": tipo_envio,
            "remitente": fila["remitente"].strip(),
            "destinatario": fila["destinatario"].strip(),
            "codigo_postal": cp,
            "tipo_servicio": servicio,
            "estado": (fila.get("estado") or "registrado").strip().lower(),
        }

        if tipo_envio != "sobre":
            try:
                peso = float(fila.get("peso", ""))
                if peso <= 0:
                    return False, "El peso debe ser mayor a 0.", None
                datos_limpios["peso"] = peso
            except ValueError:
                return False, f"Peso inválido '{fila.get('peso', '')}'.", None

            for dimension in ("largo", "ancho", "alto"):
                valor_dim = fila.get(dimension, "").strip()
                if valor_dim:
                    try:
                        dim_num = float(valor_dim)
                        if dim_num <= 0:
                            return False, f"La dimensión '{dimension}' debe ser mayor a 0.", None
                        datos_limpios[dimension] = dim_num
                    except ValueError:
                        return False, f"Dimensión '{dimension}' inválida '{valor_dim}'.", None

        if "costo" in fila and fila["costo"].strip():
            try:
                costo = float(fila["costo"].strip())
                if costo < 0:
                    return False, "El costo no puede ser negativo.", None
                datos_limpios["costo"] = costo
            except ValueError:
                return False, f"Costo inválido '{fila['costo']}'.", None
        else:
            datos_limpios["costo"] = 0.0

        return True, "", datos_limpios

    def importar_envios(self, gestor_envios: Any = None) -> list[dict[str, Any]]:
        filas = self.leer_archivo()
        self.errores.clear()
        self.envios_importados.clear()

        for indice, fila in enumerate(filas, start=2):
            es_valida, motivo, datos_limpios = self.validar_fila(fila)
            if not es_valida or datos_limpios is None:
                self.errores.append({
                    "fila": indice,
                    "motivo": motivo,
                    "datos": fila,
                })
                continue

            if gestor_envios is not None and hasattr(gestor_envios, "registrar_envio"):
                gestor_envios.registrar_envio(datos_limpios)

            self.envios_importados.append(datos_limpios)

        return self.envios_importados

    def generar_reporte_errores(self) -> str:
        if not self.errores:
            return "Sin errores: todas las filas del CSV fueron válidas."

        lineas = [f"Reporte de filas rechazadas ({len(self.errores)}):"]
        for err in self.errores:
            lineas.append(f"- Fila {err['fila']}: {err['motivo']}")
        return "\n".join(lineas)
