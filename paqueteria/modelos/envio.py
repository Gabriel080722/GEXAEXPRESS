
from abc import ABC, abstractmethod


class Envio(ABC):
    """Clase abstracta que representa un envío."""

    def __init__(
        self,
        numero_guia,
        destinatario,
        codigo_postal,
        zona,
        tipo_servicio,
        estado="registrado"
    ):
        self.numero_guia = str(numero_guia).strip()
        self.destinatario = destinatario.strip() if isinstance(destinatario, str) else ""
        self.codigo_postal = str(codigo_postal).strip()
        self.zona = zona.lower().strip() if isinstance(zona, str) and zona.strip() else None
        self.tipo_servicio = tipo_servicio.lower().strip() if isinstance(tipo_servicio, str) else ""
        self.estado = estado.lower().strip() if isinstance(estado, str) else ""
        self.costo = 0.0

        Envio.validar(self)

    def validar(self):
        """Comprueba que los datos generales del envío sean válidos."""

        if not self.numero_guia:
            raise ValueError("El número de guía es obligatorio.")

        if not self.destinatario:
            raise ValueError("El destinatario es obligatorio.")

        if not self.codigo_postal.isdigit() or len(self.codigo_postal) != 5:
            raise ValueError("El código postal debe tener cinco dígitos.")

        if self.zona is not None and self.zona not in (
            "local", "regional", "nacional"
        ):
            raise ValueError("La zona debe ser local, regional o nacional.")

        if self.tipo_servicio not in ("estandar", "express"):
            raise ValueError("El servicio debe ser estandar o express.")

        if self.estado not in (
            "registrado",
            "en almacen",
            "en ruta",
            "entregado"
        ):
            raise ValueError("El estado del envío no es válido.")

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
            "destinatario": self.destinatario,
            "codigo_postal": self.codigo_postal,
            "zona": self.zona,
            "tipo_servicio": self.tipo_servicio,
            "estado": self.estado,
            "costo": self.costo
        }


class Sobre(Envio):
    """Representa un envío de tipo sobre."""

    def calcular_costo(self, tarifas):
        """Calcula la tarifa fija del sobre según su zona."""

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
        estado="registrado"
    ):
        super().__init__(
            numero_guia,
            destinatario,
            codigo_postal,
            zona,
            tipo_servicio,
            estado
        )

        self.peso = float(peso)
        self.largo = float(largo)
        self.ancho = float(ancho)
        self.alto = float(alto)

        Paquete.validar(self)

    def validar(self):
        """Valida los datos generales y las dimensiones del paquete."""

        super().validar()

        if self.peso <= 0:
            raise ValueError("El peso debe ser mayor que cero.")

        if self.largo <= 0 or self.ancho <= 0 or self.alto <= 0:
            raise ValueError("Las dimensiones deben ser mayores que cero.")

    def calcular_peso_volumetrico(self):
        """Calcula el peso volumétrico en kilogramos."""

        return (self.largo * self.ancho * self.alto) / 5000

    def calcular_peso_facturable(self):
        """Selecciona el mayor entre el peso real y volumétrico."""

        return max(self.peso, self.calcular_peso_volumetrico())

    def calcular_costo(self, tarifas):
        """Calcula el costo del paquete según su peso facturable."""

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
        estado="registrado"
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
            estado
        )

        self.valor_declarado = float(valor_declarado)

        self.validar()

    def validar(self):
        """Valida también el valor declarado del paquete."""

        super().validar()

        if self.valor_declarado <= 0:
            raise ValueError("El valor declarado debe ser mayor que cero.")

    def calcular_costo(self, tarifas):
        """Agrega el 20 por ciento y el seguro obligatorio del 3 por ciento."""

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
        estado="registrado"
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
            estado
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
