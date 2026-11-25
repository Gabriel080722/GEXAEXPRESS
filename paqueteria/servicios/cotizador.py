
import csv
from pathlib import Path


class Cotizador:
    """Carga tarifas y calcula cotizaciones de los envíos."""

    def __init__(self, archivo_tarifas=None):
        if archivo_tarifas is None:
            raiz_proyecto = Path(__file__).resolve().parents[2]
            archivo_tarifas = raiz_proyecto / "datos" / "tarifas_zonas.csv"

        self.archivo_tarifas = Path(archivo_tarifas)
        self.tarifas = {}
        self.rangos_cp = []

        self.cargar_tarifas()

    def cargar_tarifas(self):
        """Lee las tarifas y los rangos postales desde un archivo CSV."""

        if not self.archivo_tarifas.is_file():
            raise FileNotFoundError(
                f"No se encontró el archivo: {self.archivo_tarifas}"
            )

        tarifas = {}
        rangos = []

        columnas = {
            "cp_inicio",
            "cp_fin",
            "zona",
            "tarifa_sobre",
            "tarifa_paquete_kg"
        }

        with self.archivo_tarifas.open(
            "r", encoding="utf-8-sig", newline=""
        ) as archivo:

            lector = csv.DictReader(archivo)

            if not lector.fieldnames or not columnas.issubset(lector.fieldnames):
                raise ValueError(
                    "El CSV debe contener: cp_inicio, cp_fin, zona, "
                    "tarifa_sobre y tarifa_paquete_kg."
                )

            for numero_fila, fila in enumerate(lector, start=2):
                try:
                    inicio = fila["cp_inicio"].strip()
                    fin = fila["cp_fin"].strip()
                    zona = fila["zona"].strip().lower()

                    if (
                        len(inicio) != 5 or not inicio.isdigit()
                        or len(fin) != 5 or not fin.isdigit()
                    ):
                        raise ValueError("El rango postal debe tener cinco dígitos.")

                    inicio_num = int(inicio)
                    fin_num = int(fin)

                    if inicio_num > fin_num:
                        raise ValueError("El código postal inicial supera al final.")

                    if zona not in ("local", "regional", "nacional"):
                        raise ValueError("La zona no es válida.")

                    tarifa_sobre = float(fila["tarifa_sobre"])
                    tarifa_paquete = float(fila["tarifa_paquete_kg"])

                    if tarifa_sobre <= 0 or tarifa_paquete <= 0:
                        raise ValueError("Las tarifas deben ser mayores que cero.")

                    if zona in tarifas:
                        if tarifas[zona] != {
                            "tarifa_sobre": tarifa_sobre,
                            "tarifa_paquete_kg": tarifa_paquete
                        }:
                            raise ValueError(
                                "Una misma zona no puede tener tarifas diferentes."
                            )
                    else:
                        tarifas[zona] = {
                            "tarifa_sobre": tarifa_sobre,
                            "tarifa_paquete_kg": tarifa_paquete
                        }

                    rangos.append((inicio_num, fin_num, zona))

                except (ValueError, TypeError) as error:
                    raise ValueError(
                        f"Error en la fila {numero_fila} del CSV: {error}"
                    ) from error

        if not rangos:
            raise ValueError("El archivo de tarifas no contiene registros.")

        rangos.sort(key=lambda rango: rango[0])

        for anterior, actual in zip(rangos, rangos[1:]):
            if actual[0] <= anterior[1]:
                raise ValueError("Existen rangos de códigos postales superpuestos.")

        self.tarifas = tarifas
        self.rangos_cp = rangos

        return self.tarifas

    def obtener_zona(self, codigo_postal):
        """Determina la zona correspondiente al código postal."""

        codigo_postal = str(codigo_postal).strip()

        if len(codigo_postal) != 5 or not codigo_postal.isdigit():
            raise ValueError("El código postal debe tener cinco dígitos.")

        codigo = int(codigo_postal)

        for inicio, fin, zona in self.rangos_cp:
            if inicio <= codigo <= fin:
                return zona

        raise ValueError(
            f"No existe una zona registrada para el código postal {codigo_postal}."
        )

    def calcular_cotizacion(self, envio):
        """Determina la zona y calcula el costo total del envío."""

        if not self.tarifas:
            self.cargar_tarifas()

        zona = self.obtener_zona(envio.codigo_postal)

        envio.zona = zona
        envio.validar()

        costo = envio.calcular_costo(self.tarifas)

        return round(costo, 2)
