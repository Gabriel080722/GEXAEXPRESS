
import unittest
from types import SimpleNamespace

from paqueteria.modelos.repartidor import Vehiculo, Repartidor


class TestVehiculo(unittest.TestCase):
    """Pruebas de la clase Vehiculo."""

    def test_crear_motocicleta(self):
        vehiculo = Vehiculo("motocicleta")
        self.assertEqual(vehiculo.capacidad_maxima, 20)

    def test_crear_camioneta(self):
        vehiculo = Vehiculo("camioneta")
        self.assertEqual(vehiculo.capacidad_maxima, 500)

    def test_tipo_invalido(self):
        with self.assertRaises(ValueError):
            Vehiculo("bicicleta")

    def test_tipo_vacio(self):
        with self.assertRaises(ValueError):
            Vehiculo("")

    def test_capacidad_permitida(self):
        vehiculo = Vehiculo("motocicleta")
        self.assertTrue(vehiculo.verificar_capacidad(15))

    def test_capacidad_exacta(self):
        vehiculo = Vehiculo("motocicleta")
        self.assertTrue(vehiculo.verificar_capacidad(20))

    def test_capacidad_excedida(self):
        vehiculo = Vehiculo("motocicleta")
        self.assertFalse(vehiculo.verificar_capacidad(25))

    def test_peso_negativo(self):
        vehiculo = Vehiculo("motocicleta")
        with self.assertRaises(ValueError):
            vehiculo.verificar_capacidad(-5)

    def test_peso_no_numerico(self):
        vehiculo = Vehiculo("camioneta")
        with self.assertRaises(ValueError):
            vehiculo.verificar_capacidad("veinte")


class TestRepartidor(unittest.TestCase):
    """Pruebas de la clase Repartidor."""

    def setUp(self):
        self.vehiculo = Vehiculo("motocicleta")
        self.repartidor = Repartidor(
            "R001",
            "Carlos",
            self.vehiculo
        )

    def crear_envio(self, peso, estado="en almacen", guia="G001"):
        return SimpleNamespace(
            peso_real=peso,
            estado=estado,
            numero_guia=guia
        )

    def test_crear_repartidor(self):
        self.assertEqual(self.repartidor.identificador, "R001")
        self.assertEqual(self.repartidor.nombre, "Carlos")

    def test_nombre_vacio(self):
        with self.assertRaises(ValueError):
            Repartidor("R002", "", self.vehiculo)

    def test_identificador_vacio(self):
        with self.assertRaises(ValueError):
            Repartidor("", "Carlos", self.vehiculo)

    def test_vehiculo_invalido(self):
        with self.assertRaises(ValueError):
            Repartidor("R003", "Ana", "motocicleta")

    def test_asignar_envio(self):
        envio = self.crear_envio(10)
        resultado = self.repartidor.asignar_envio(envio)

        self.assertTrue(resultado)
        self.assertEqual(len(self.repartidor.consultar_envios()), 1)

    def test_calcular_carga(self):
        self.repartidor.asignar_envio(self.crear_envio(5))
        self.repartidor.asignar_envio(
            self.crear_envio(10, guia="G002")
        )

        self.assertEqual(self.repartidor.calcular_carga(), 15)

    def test_rechazar_exceso_de_capacidad(self):
        envio = self.crear_envio(21)

        with self.assertRaises(ValueError):
            self.repartidor.asignar_envio(envio)

    def test_rechazar_envio_duplicado(self):
        envio = self.crear_envio(5)
        self.repartidor.asignar_envio(envio)

        with self.assertRaises(ValueError):
            self.repartidor.asignar_envio(envio)

    def test_rechazar_envio_fuera_de_almacen(self):
        envio = self.crear_envio(5, estado="en ruta")

        with self.assertRaises(ValueError):
            self.repartidor.asignar_envio(envio)

    def test_rechazar_envio_vacio(self):
        with self.assertRaises(ValueError):
            self.repartidor.asignar_envio(None)

    def test_consultar_envios(self):
        envio = self.crear_envio(8)
        self.repartidor.asignar_envio(envio)

        resultado = self.repartidor.consultar_envios()

        self.assertEqual(len(resultado), 1)
        self.assertIs(resultado[0], envio)

    def test_consultar_envios_no_modifica_lista_original(self):
        self.repartidor.asignar_envio(self.crear_envio(5))

        resultado = self.repartidor.consultar_envios()
        resultado.clear()

        self.assertEqual(len(self.repartidor.consultar_envios()), 1)


if __name__ == "__main__":
    unittest.main()
