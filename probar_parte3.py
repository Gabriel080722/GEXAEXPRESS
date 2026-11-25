from pathlib import Path
from paqueteria.persistencia.almacenamiento import Almacenamiento
from paqueteria.servicios.importador_csv import ImportadorCSV
from paqueteria.servicios.reportes import Reportes

csv_prueba = Path("datos/prueba_envios.csv")
csv_prueba.write_text(
    "tipo_envio,remitente,destinatario,codigo_postal,tipo_servicio,peso,costo,estado\n"
    "sobre,Empresa A,Cliente 1,01000,expres,,150.0,entregado\n"
    "paquete,Empresa A,Cliente 2,ABC12,estandar,2.5,300.0,registrado\n"
    "paquete,Empresa B,Cliente 3,14000,expres,4.0,450.0,entregado\n",
    encoding="utf-8",
)

importador = ImportadorCSV(csv_prueba)
importados = importador.importar_envios()
print("Importados:", len(importados))
print(importador.generar_reporte_errores())

alm = Almacenamiento(
    archivo_envios="datos/test_envios.json",
    archivo_repartidores="datos/test_repartidores.json",
    archivo_historiales="datos/test_historiales.json",
)
alm.guardar_envios(importados)
print("Cargados desde JSON:", len(alm.cargar_envios()))

rep = Reportes(archivo_salida="datos/test_reporte.json")
reporte = rep.generar_reporte_diario(
    importados,
    [{"identificador": "R1", "envios_asignados": [importados[0]]}],
)
rep.guardar_reporte(reporte)
print("Reporte generado:", reporte)