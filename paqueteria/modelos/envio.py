from abc import ABC, abstractmethod
import math


class Envio(ABC):
    """Clase abstracta que representa un envío."""

    ESTADOS_VALIDOS = (
        "registrado",
        "en almacen",
        "en ruta",
        "entregado",
        "cancelado",
        "devuelto al remitente"
    )

    def __init__(
        self,
        numero_guia,
        destinatario,
        codigo_postal,
        zona,
        tipo_servicio,
        estado="registrado",
        remitente=""
    ):
        self.numero_guia = str(numero_guia).strip()
        self.remitente = remitente.strip() if isinstance(remitente, str) else ""
        self.destinatario = (
            destinatario.strip() if isinstance(destinatario, str) else ""
        )
        self.codigo_postal = str(codigo_postal).strip()
        self.zona = (
            zona.lower().strip()
            if isinstance(zona, str) and zona.strip()
            else None
        )
        self.tipo_servicio = (
            tipo_servicio.lower().strip()
            if isinstance(tipo_servicio, str)
            else ""
        )
        self.estado = (
            estado.lower().strip()
            if isinstance(estado, str)
            else ""
        )

        self.costo = 0.0
        self.intentos_fallidos = 0

    def validar(self):
        """Comprueba que los datos generales sean válidos."""

        if not self.numero_guia:
            raise ValueError("El número de guía es obligatorio.")

        if not self.destinatario:
            raise ValueError("El destinatario es obligatorio.")

        if (
            len(self.codigo_postal) != 5
            or not self.codigo_postal.isdigit()
        ):
            raise ValueError("El código postal debe tener cinco dígitos.")

        if self.zona is not None and self.zona not in (
            "local", "regional", "nacional"
        ):
            raise ValueError("La zona debe ser local, regional o nacional.")

        if self.tipo_servicio not in ("estandar", "express"):
            raise ValueError("El servicio debe ser estandar o express.")

        if self.estado not in self.ESTADOS_VALIDOS:
            raise ValueError("El estado del envío no es válido.")

        if (
            isinstance(self.intentos_fallidos, bool)
            or not isinstance(self.intentos_fallidos, int)
            or self.intentos_fallidos < 0
        ):
            raise ValueError(
                "Los intentos fallidos deben ser un entero no negativo."
            )

    def aplicar_servicio(self, costo_base):
        """Aplica el incremento del servicio express."""

        if self.tipo_servicio == "express":
            return costo_base * 1.50

        return costo_base

    @abstractmethod
    def calcular_costo(self, tarifas):
        """Calcula el costo según el tipo de envío."""
        pass

    def obtener_informacion(self):
        """Devuelve la información general del envío."""

        return {
            "numero_guia": self.numero_guia,
            "remitente": self.remitente,
            "destinatario": self.destinatario,
            "codigo_postal": self.codigo_postal,
            "zona": self.zona,
            "tipo_servicio": self.tipo_servicio,
            "estado": self.estado,
            "costo": self.costo,
            "intentos_fallidos": self.intentos_fallidos
        }


class Sobre(Envio):
    """Representa un envío de tipo sobre."""

    def __init__(
        self,
        numero_guia,
        destinatario,
        codigo_postal,
        zona,
        tipo_servicio,
        estado="registrado",
        remitente="",
        peso=None
    ):
        super().__init__(
            numero_guia,
            destinatario,
            codigo_postal,
            zona,
            tipo_servicio,
            estado,
            remitente
        )

        self.peso = None
        self.peso_real = None

        if peso is not None:
            self.establecer_peso_fisico(peso)

        self.validar()

    def establecer_peso_fisico(self, peso):
        """Registra y valida el peso físico del sobre."""

        if isinstance(peso, bool):
            raise ValueError("El peso del sobre debe ser un número válido.")

        try:
            numero = float(peso)
        except (TypeError, ValueError):
            raise ValueError("El peso del sobre debe ser un número válido.")

        if not math.isfinite(numero) or numero <= 0:
            raise ValueError("El peso del sobre debe ser mayor que cero.")

        self.peso = numero
        self.peso_real = numero

    def calcular_costo(self, tarifas):
        """Calcula la tarifa fija del sobre según su zona."""

        if self.zona not in tarifas:
            raise ValueError("No existen tarifas para la zona del envío.")

        tarifa = tarifas[self.zona]["tarifa_sobre"]
        self.costo = self.aplicar_servicio(tarifa)

        return self.costo


class Paquete(Envio):
    """Representa un paquete con peso y dimensiones."""

    def __init__(
        self,
        numero_guia,
        destinatario,
        codigo_postal,
        zona,
        tipo_servicio,
        peso,
        largo,
        ancho,
        alto,
        estado="registrado",
        remitente=""
    ):
        super().__init__(
            numero_guia,
            destinatario,
            codigo_postal,
            zona,
            tipo_servicio,
            estado,
            remitente
        )

        self.peso = self._validar_numero(peso, "El peso")
        self.peso_real = self.peso
        self.largo = self._validar_numero(largo, "El largo")
        self.ancho = self._validar_numero(ancho, "El ancho")
        self.alto = self._validar_numero(alto, "El alto")

        self.validar()

    @staticmethod
    def _validar_numero(valor, nombre):
        """Convierte y valida un valor numérico positivo."""

        if isinstance(valor, bool):
            raise ValueError(f"{nombre} debe ser un número válido.")

        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError(f"{nombre} debe ser un número válido.")

        if not math.isfinite(numero) or numero <= 0:
            raise ValueError(f"{nombre} debe ser mayor que cero.")

        return numero

    def validar(self):
        """Valida los datos generales y las dimensiones."""

        super().validar()

        for valor, nombre in (
            (self.peso, "El peso"),
            (self.largo, "El largo"),
            (self.ancho, "El ancho"),
            (self.alto, "El alto")
        ):
            if (
                isinstance(valor, bool)
                or not isinstance(valor, (int, float))
                or not math.isfinite(valor)
                or valor <= 0
            ):
                raise ValueError(f"{nombre} debe ser mayor que cero.")

    def calcular_peso_volumetrico(self):
        """Calcula el peso volumétrico en kilogramos."""

        return (self.largo * self.ancho * self.alto) / 5000

    def calcular_peso_facturable(self):
        """Selecciona el mayor entre el peso real y volumétrico."""

        return max(self.peso, self.calcular_peso_volumetrico())

    def calcular_costo(self, tarifas):
        """Calcula el costo del paquete según su peso facturable."""

        if self.zona not in tarifas:
            raise ValueError("No existen tarifas para la zona del envío.")

        tarifa_kg = tarifas[self.zona]["tarifa_paquete_kg"]
        costo_base = self.calcular_peso_facturable() * tarifa_kg

        self.costo = self.aplicar_servicio(costo_base)

        return self.costo


class PaqueteFragil(Paquete):
    """Representa un paquete que requiere manejo especial y seguro."""

    def __init__(
        self,
        numero_guia,
        destinatario,
        codigo_postal,
        zona,
        tipo_servicio,
        peso,
        largo,
        ancho,
        alto,
        valor_declarado,
        estado="registrado",
        remitente=""
    ):
        super().__init__(
            numero_guia,
            destinatario,
            codigo_postal,
            zona,
            tipo_servicio,
            peso,
            largo,
            ancho,
            alto,
            estado,
            remitente
        )

        self.valor_declarado = self._validar_numero(
            valor_declarado,
            "El valor declarado"
        )

        self.validar()

    def validar(self):
        """Valida también el valor declarado."""

        super().validar()

        if hasattr(self, "valor_declarado"):
            if (
                not math.isfinite(self.valor_declarado)
                or self.valor_declarado <= 0
            ):
                raise ValueError(
                    "El valor declarado debe ser mayor que cero."
                )

    def calcular_costo(self, tarifas):
        """Agrega el 20 por ciento y el seguro obligatorio del 3 por ciento."""

        if self.zona not in tarifas:
            raise ValueError("No existen tarifas para la zona del envío.")

        tarifa_kg = tarifas[self.zona]["tarifa_paquete_kg"]
        costo_base = self.calcular_peso_facturable() * tarifa_kg

        costo_fragil = costo_base * 1.20
        seguro = self.valor_declarado * 0.03

        self.costo = self.aplicar_servicio(costo_fragil + seguro)

        return self.costo

    def obtener_informacion(self):
        """Devuelve los datos generales y el valor declarado."""

        informacion = super().obtener_informacion()
        informacion["valor_declarado"] = self.valor_declarado

        return informacion


class PaqueteRefrigerado(Paquete):
    """Representa un paquete que necesita refrigeración."""

    def __init__(
        self,
        numero_guia,
        destinatario,
        codigo_postal,
        zona,
        tipo_servicio,
        peso,
        largo,
        ancho,
        alto,
        estado="registrado",
        remitente=""
    ):
        super().__init__(
            numero_guia,
            destinatario,
            codigo_postal,
            zona,
            tipo_servicio,
            peso,
            largo,
            ancho,
            alto,
            estado,
            remitente
        )

        self.validar()

    def validar(self):
        """Comprueba que sea express y que no tenga destino nacional."""

        super().validar()

        if self.tipo_servicio != "express":
            raise ValueError(
                "Los paquetes refrigerados solo admiten servicio express."
            )

        if self.zona == "nacional":
            raise ValueError(
                "Los paquetes refrigerados no pueden enviarse a zona nacional."
            )

    def calcular_costo(self, tarifas):
        """Calcula el costo del paquete refrigerado."""

        return super().calcular_costo(tarifas)