from datetime import datetime


class Historial:
    """Registra los movimientos de un envío."""

    def __init__(self, numero_guia):
        if not isinstance(numero_guia, str) or not numero_guia.strip():
            raise ValueError("El número de guía es obligatorio.")

        self.numero_guia = numero_guia.strip()
        self.movimientos = []

    def registrar_movimiento(self, estado, fecha_hora=None):
        """Agrega un cambio de estado al historial."""

        if not isinstance(estado, str) or not estado.strip():
            raise ValueError("El estado es obligatorio.")

        if fecha_hora is None:
            fecha_hora = datetime.now()

        if isinstance(fecha_hora, datetime):
            fecha_hora = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        elif not isinstance(fecha_hora, str):
            raise ValueError("La fecha y hora no son válidas.")

        movimiento = {
            "estado": estado.strip().lower(),
            "fecha_hora": fecha_hora
        }

        self.movimientos.append(movimiento)
        return movimiento

    def obtener_historial(self):
        """Devuelve una copia de los movimientos registrados."""
        return self.movimientos.copy()

    def obtener_ultimo_estado(self):
        """Devuelve el estado más reciente."""
        if not self.movimientos:
            return None

        return self.movimientos[-1]["estado"]