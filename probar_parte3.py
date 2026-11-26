from pathlib import Path
from tempfile import TemporaryDirectory

from paqueteria.persistencia.almacenamiento import Almacenamiento
from paqueteria.servicios.importador_csv import ImportadorCSV
from paqueteria.servicios.reportes import Reportes


def main():
    with TemporaryDirectory() as temporal:
        carpeta = Path(temporal)

        # Crear archivo CSV de prueba.
        csv_prueba = carpeta / "prueba_envios.csv"

        csv_prueba.write_text(
            "tipo_envio,numero_guia,remitente,destinatario,codigo_postal,"
            "tipo_servicio,peso,largo,ancho,alto,valor_declarado,estado\n"
            "sobre,GEX001,Empresa A,Cliente 1,01000,expres,,,,,,entregado\n"
            "paquete,GEX002,Empresa B,Cliente 2,14000,estandar,2.5,20,15,10,,registrado\n"
            "paquetefragil,GEX003,Empresa C,Cliente 3,30000,estandar,2,10,10,10,500,registrado\n"
            "paqueterefrigerado,GEX004,Empresa D,Cliente 4,30000,express,2,10,10,10,,registrado\n"
            "paquete,GEX005,Empresa E,Cliente 5,ABC12,estandar,4,20,15,10,,registrado\n",
            encoding="utf-8",
        )

        # Importar envíos.
        importador = ImportadorCSV(csv_prueba)
        importados = importador.importar_envios()

        print("Importados:", len(importados))
        print(importador.generar_reporte_errores())

        # Probar persistencia JSON.
        alm = Almacenamiento(
            archivo_envios=carpeta / "test_envios.json",
            archivo_repartidores=carpeta / "test_repartidores.json",
            archivo_historiales=carpeta / "test_historiales.json",
        )

        alm.guardar_envios(importados)
        cargados = alm.cargar_envios()

        print("Cargados desde JSON:", len(cargados))

        # Probar generación de reportes.
        rep = Reportes(archivo_salida=carpeta / "test_reporte.json")

        reporte = rep.generar_reporte_diario(
            importados,
            [{
                "identificador": "R1",
                "envios_asignados": [importados[0]],
            }],
        )

        rep.guardar_reporte(reporte)

        print("Reporte generado:", reporte)


if __name__ == "__main__":
    main()