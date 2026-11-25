
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from paqueteria.modelos.repartidor import Vehiculo, Repartidor
from paqueteria.servicios.simulador import Simulador


class GeneradorPrueba:
    """Generador de resultados controlados para las pruebas."""

    def __init__(self, resultados=None):
        self.resultados = iter(resultados or [])

    def random(self):
        return next(self.resultados)

    def uniform(self, minimo, maximo):
        return minimo


class TestSimulador(unittest.TestCase):
    """Pruebas de la clase Simulador."""

    def setUp(self):
        self.vehiculo = Vehiculo("camioneta")

        self.repartidor = Repartidor(
            "R001",
            "Carlos",
            self.vehiculo
        )

        self.envio = SimpleNamespace(
            numero_guia="G001",
            peso_real=10,
            estado="en almacen"
        )

        self.repartidor.asignar_envio(self.envio)

    def crear_simulador(self, resultados):
        generador = GeneradorPrueba(resultados)

        return Simulador(
            [self.repartidor],
            duracion_jornada=10,
            tiempo_minimo=0.01,
            tiempo_maximo=0.01,
            generador=generador
        )

    def test_crear_simulador(self):
        simulador = self.crear_simulador([0.50])

        self.assertEqual(len(simulador.repartidores), 1)
        self.assertEqual(simulador.duracion_jornada, 10)

    def test_lista_de_repartidores_vacia(self):
        with self.assertRaises(ValueError):
            Simulador([], 10)

    def test_duracion_invalida(self):
        with self.assertRaises(ValueError):
            Simulador([self.repartidor], 0)

    def test_entrega_exitosa(self):
        simulador = self.crear_simulador([0.50])

        resultado = simulador.simular_entrega(
            self.repartidor,
            self.envio
        )

        self.assertTrue(resultado)
        self.assertEqual(self.envio.estado, "entregado")

    def test_entrega_fallida(self):
        simulador = self.crear_simulador([0.05])

        resultado = simulador.simular_entrega(
            self.repartidor,
            self.envio
        )

        self.assertFalse(resultado)
        self.assertEqual(self.envio.estado, "en almacen")

    def test_tres_intentos_fallidos(self):
        simulador = self.crear_simulador([0.05, 0.05, 0.05])

        for intento in range(3):
            simulador.simular_entrega(
                self.repartidor,
                self.envio
            )

        self.assertEqual(
            self.envio.estado,
            "devuelto al remitente"
        )

        self.assertEqual(
            simulador.intentos_fallidos["G001"],
            3
        )

    def test_registrar_resultado(self):
        simulador = self.crear_simulador([0.50])

        simulador.simular_entrega(
            self.repartidor,
            self.envio
        )

        self.assertEqual(len(simulador.resultados), 1)

        self.assertEqual(
            simulador.resultados[0]["resultado"],
            "exitoso"
        )

    def test_rechazar_repartidor_no_asignado(self):
        simulador = self.crear_simulador([0.50])

        otro = Repartidor(
            "R002",
            "Ana",
            Vehiculo("motocicleta")
        )

        with self.assertRaises(ValueError):
            simulador.simular_entrega(otro, self.envio)

    def test_rechazar_envio_no_asignado(self):
        simulador = self.crear_simulador([0.50])

        otro_envio = SimpleNamespace(
            numero_guia="G002",
            peso_real=5,
            estado="en almacen"
        )

        with self.assertRaises(ValueError):
            simulador.simular_entrega(
                self.repartidor,
                otro_envio
            )

    def test_iniciar_simulacion(self):
        simulador = self.crear_simulador([0.50])

        with patch("paqueteria.servicios.simulador.time.sleep"):
            resultados = simulador.iniciar_simulacion()

        self.assertEqual(len(resultados), 1)
        self.assertEqual(self.envio.estado, "entregado")

    def test_simulacion_no_se_inicia_dos_veces(self):
        simulador = self.crear_simulador([0.50])

        with patch("paqueteria.servicios.simulador.time.sleep"):
            simulador.iniciar_simulacion()

        with self.assertRaises(RuntimeError):
            simulador.iniciar_simulacion()

    def test_mostrar_progreso(self):
        simulador = self.crear_simulador([0.50])

        with patch("builtins.print") as impresion:
            simulador.mostrar_progreso()

        impresion.assert_called()

    def test_dos_repartidores_simultaneos(self):
        repartidor2 = Repartidor(
            "R002",
            "Ana",
            Vehiculo("camioneta")
        )

        envio2 = SimpleNamespace(
            numero_guia="G002",
            peso_real=15,
            estado="en almacen"
        )

        repartidor2.asignar_envio(envio2)

        simulador = Simulador(
            [self.repartidor, repartidor2],
            duracion_jornada=10,
            tiempo_minimo=0.01,
            tiempo_maximo=0.01,
            generador=GeneradorPrueba([0.50, 0.50])
        )

        with patch("paqueteria.servicios.simulador.time.sleep"):
            simulador.iniciar_simulacion()

        self.assertEqual(self.envio.estado, "entregado")
        self.assertEqual(envio2.estado, "entregado")

        self.assertEqual(len(simulador.progreso), 2)


if __name__ == "__main__":
    unittest.main()
