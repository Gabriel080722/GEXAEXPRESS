
import unittest

from paqueteria.servicios.cotizador import Cotizador
from paqueteria.modelos.envio import Sobre, Paquete


class TestCotizador(unittest.TestCase):

    def setUp(self):
        self.cotizador = Cotizador()

    def test_cargar_tarifas(self):
        self.assertIn("local", self.cotizador.tarifas)
        self.assertIn("regional", self.cotizador.tarifas)
        self.assertIn("nacional", self.cotizador.tarifas)

    def test_obtener_zona_local(self):
        self.assertEqual(
            self.cotizador.obtener_zona("12345"), "local"
        )

    def test_obtener_zona_regional(self):
        self.assertEqual(
            self.cotizador.obtener_zona("25000"), "regional"
        )

    def test_obtener_zona_nacional(self):
        self.assertEqual(
            self.cotizador.obtener_zona("55000"), "nacional"
        )

    def test_codigo_postal_invalido(self):
        with self.assertRaises(ValueError):
            self.cotizador.obtener_zona("ABC")

    def test_cotizacion_sobre(self):
        sobre = Sobre(
            "101", "Ana", "12345", None, "estandar"
        )

        resultado = self.cotizador.calcular_cotizacion(sobre)

        self.assertEqual(resultado, 50)
        self.assertEqual(sobre.zona, "local")

    def test_cotizacion_paquete_express(self):
        paquete = Paquete(
            "102", "Luis", "25000", None, "express",
            2, 10, 10, 10
        )

        resultado = self.cotizador.calcular_cotizacion(paquete)

        self.assertEqual(resultado, 120)
        self.assertEqual(paquete.zona, "regional")


if __name__ == "__main__":
    unittest.main()
