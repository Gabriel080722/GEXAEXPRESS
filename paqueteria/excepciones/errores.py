class GexaExpressError(Exception):
    """Error base del sistema GexaExpress."""


class EnvioInvalidoError(GexaExpressError):
    """Se lanza cuando los datos o reglas de un envío no son válidos."""


class EstadoInvalidoError(GexaExpressError):
    """Se lanza cuando se intenta una transición de estado no permitida."""


class CapacidadExcedidaError(GexaExpressError):
    """Se lanza cuando se excede la capacidad máxima de un vehículo o repartidor."""


class ArchivoInvalidoError(GexaExpressError):
    """Se lanza cuando un archivo no existe, no se puede leer o tiene formato inválido."""
