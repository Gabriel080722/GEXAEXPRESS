
import unittest

from paqueteria.modelos.envio import (
    Sobre,
    Paquete,
    PaqueteFragil,
    PaqueteRefrigerado
)


class TestEnvios(unittest.TestCase):

    def setUp(self):
        self.tarifas = {
            "local": {
                "tarifa_sobre": 50,
                "tarifa_paquete_kg": 30
            },
            "regional": {
                "tarifa_sobre": 80,
                "tarifa_paquete_kg": 40
            },
            "nacional": {
                "tarifa_sobre": 120,
                "tarifa_paquete_kg": 55
            }
        }

    def test_costo_sobre(self):
        sobre = Sobre(
            "001", "Ana", "12345", "local", "estandar"
        )
        self.assertEqual(sobre.calcular_costo(self.tarifas), 50)

    def test_costo_sobre_express(self):
        sobre = Sobre(
            "002", "Ana", "12345", "local", "express"
        )
        self.assertEqual(sobre.calcular_costo(self.tarifas), 75)

    def test_peso_volumetrico(self):
        paquete = Paquete(
            "003", "Luis", "12345", "local", "estandar",
            2, 10, 10, 10
        )
        self.assertEqual(paquete.calcular_peso_volumetrico(), 0.2)

    def test_peso_facturable(self):
        paquete = Paquete(
            "004", "Luis", "12345", "local", "estandar",
            2, 100, 100, 100
        )
        self.assertEqual(paquete.calcular_peso_facturable(), 200)

    def test_costo_paquete(self):
        paquete = Paquete(
            "005", "Luis", "12345", "local", "estandar",
            2, 10, 10, 10
        )
        self.assertEqual(paquete.calcular_costo(self.tarifas), 60)

    def test_costo_paquete_fragil(self):
        paquete = PaqueteFragil(
            "006", "Maria", "12345", "local", "estandar",
            2, 10, 10, 10, 1000
        )
        self.assertEqual(paquete.calcular_costo(self.tarifas), 102)

    def test_refrigerado_valido(self):
        paquete = PaqueteRefrigerado(
            "007", "Carlos", "25000", "regional", "express",
            2, 10, 10, 10
        )
        self.assertEqual(paquete.calcular_costo(self.tarifas), 120)

    def test_peso_negativo(self):
        with self.assertRaises(ValueError):
            Paquete(
                "008", "Luis", "12345", "local", "estandar",
                -2, 10, 10, 10
            )

    def test_dimensiones_invalidas(self):
        with self.assertRaises(ValueError):
            Paquete(
                "009", "Luis", "12345", "local", "estandar",
                2, 0, 10, 10
            )

    def test_refrigerado_estandar(self):
        with self.assertRaises(ValueError):
            PaqueteRefrigerado(
                "010", "Carlos", "25000", "regional", "estandar",
                2, 10, 10, 10
            )

    def test_refrigerado_nacional(self):
        with self.assertRaises(ValueError):
            PaqueteRefrigerado(
                "011", "Carlos", "55000", "nacional", "express",
                2, 10, 10, 10
            )


if __name__ == "__main__":
    unittest.main()
