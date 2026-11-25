
from threading import RLock


class Vehiculo:
    """Representa el vehículo asignado a un repartidor."""

    CAPACIDADES = {
        "motocicleta": 20,
        "camioneta": 500
    }

    def __init__(self, tipo):
        """Inicializa el vehículo y establece su capacidad máxima."""
        if not isinstance(tipo, str) or not tipo.strip():
            raise ValueError("El tipo de vehículo debe ser válido.")

        tipo = tipo.strip().lower()

        if tipo not in self.CAPACIDADES:
            raise ValueError(
                "El vehículo debe ser motocicleta o camioneta."
            )

        self.tipo = tipo
        self.capacidad_maxima = self.CAPACIDADES[tipo]

    def verificar_capacidad(self, peso_total):
        """Comprueba que la carga no supere la capacidad del vehículo."""
        if isinstance(peso_total, bool) or not isinstance(peso_total, (int, float)):
            raise ValueError("El peso debe ser numérico.")

        if peso_total < 0:
            raise ValueError("El peso no puede ser negativo.")

        return peso_total <= self.capacidad_maxima


class Repartidor:
    """Representa a un repartidor y administra sus envíos asignados."""

    def __init__(self, identificador, nombre, vehiculo):
        """Inicializa un repartidor con su identificador y vehículo."""
        if not isinstance(identificador, str) or not identificador.strip():
            raise ValueError("El identificador es obligatorio.")

        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del repartidor es obligatorio.")

        if not isinstance(vehiculo, Vehiculo):
            raise ValueError("Debe asignarse un vehículo válido.")

        self.identificador = identificador.strip()
        self.nombre = nombre.strip()
        self.vehiculo = vehiculo
        self.envios_asignados = []
        self._lock = RLock()

    def _obtener_peso(self, envio):
        """Obtiene el peso real del envío para calcular la carga física."""
        if hasattr(envio, "peso_real"):
            peso = envio.peso_real
        elif hasattr(envio, "peso"):
            peso = envio.peso
        else:
            raise ValueError("El envío no tiene un atributo de peso real.")

        if isinstance(peso, bool) or not isinstance(peso, (int, float)):
            raise ValueError("El peso del envío debe ser numérico.")

        if peso <= 0:
            raise ValueError("El peso del envío debe ser mayor que cero.")

        return peso

    def asignar_envio(self, envio):
        """Asigna un envío en almacén sin superar la capacidad del vehículo."""
        if envio is None:
            raise ValueError("No se puede asignar un envío vacío.")

        with self._lock:
            if envio in self.envios_asignados:
                raise ValueError("El envío ya está asignado a este repartidor.")

            guia = getattr(envio, "numero_guia", None)

            if guia is not None:
                for asignado in self.envios_asignados:
                    if getattr(asignado, "numero_guia", None) == guia:
                        raise ValueError("La guía ya está asignada.")

            estado = getattr(envio, "estado", None)

            if not isinstance(estado, str):
                raise ValueError("El envío no tiene un estado válido.")

            estado = estado.strip().lower().replace("_", " ")

            if estado not in ("en almacen", "en almacén"):
                raise ValueError("Solo se pueden asignar envíos en almacén.")

            peso = self._obtener_peso(envio)
            nueva_carga = self.calcular_carga() + peso

            if not self.vehiculo.verificar_capacidad(nueva_carga):
                raise ValueError(
                    f"Capacidad excedida. El vehículo admite "
                    f"{self.vehiculo.capacidad_maxima} kg y la carga "
                    f"sería de {nueva_carga} kg."
                )

            self.envios_asignados.append(envio)
            return True

    def calcular_carga(self):
        """Calcula el peso real total de los envíos asignados."""
        with self._lock:
            return sum(
                self._obtener_peso(envio)
                for envio in self.envios_asignados
            )

    def consultar_envios(self):
        """Devuelve una copia de los envíos asignados."""
        with self._lock:
            return self.envios_asignados.copy()
