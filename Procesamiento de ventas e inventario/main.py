import os
import sys

from calculos import formatear_monto
from datos import (ErrorArchivo, actualizar_inventario, cargar_productos,
                   cargar_vendedores, cargar_ventas, leer_json)
from ordenamiento import ordenar_ventas
from procesamiento import procesar_ventas
from reportes import (COLUMNAS_RECHAZADAS, COLUMNAS_RESUMEN, COLUMNAS_VENTAS,
                      agrupar_por_vendedor, escribir_csv, escribir_inventario,
                      fila_rechazada, filas_de_venta, filas_resumen)

ARCHIVO_INVENTARIO = "inventario.json"
ARCHIVO_VENTAS = "ventas.json"
CARPETA_SALIDAS = "salidas"

ORDENES = {
    "1": ("fecha", "asc"),
    "2": ("total", "asc"),
    "3": ("id_venta", "asc"),
    "4": ("fecha", "desc"),
    "5": ("total", "desc"),
    "6": ("id_venta", "desc"),
}


def preguntar_separador():
    while True:
        try:
            respuesta = input("Separador de los CSV, coma (,) o punto y coma (;): ").strip()
        except EOFError:
            print("No hay consola, se usa la coma.")
            return ","
        if respuesta == "," or respuesta == ";":
            return respuesta
        if respuesta == "":
            return ","
        print("   Opcion invalida, solo ',' o ';'.")


def preguntar_orden():
    print("")
    print("Como ordenar las ventas de cada vendedor:")
    print("   1) por fecha, ascendente         4) por fecha, descendente")
    print("   2) por total, ascendente         5) por total, descendente")
    print("   3) por id de venta, ascendente   6) por id de venta, descendente")
    while True:
        try:
            respuesta = input("Opcion: ").strip()
        except EOFError:
            print("No hay consola, se ordena por fecha ascendente.")
            return "fecha", "asc"
        if respuesta == "":
            return "fecha", "asc"
        if respuesta in ORDENES:
            return ORDENES[respuesta]
        print("   Opcion invalida, se espera un numero del 1 al 6.")


def ejecutar(carpeta):
    # primero los datos, para no preguntar nada si despues no se puede seguir
    datos_inventario = leer_json(os.path.join(carpeta, ARCHIVO_INVENTARIO))
    datos_ventas = leer_json(os.path.join(carpeta, ARCHIVO_VENTAS))

    productos = cargar_productos(datos_inventario)
    if not productos:
        raise ErrorArchivo(ARCHIVO_INVENTARIO + " no tiene ningun producto cargado.")

    # los vendedores vienen en el archivo de ventas, pero por si el profesor los
    # mueve de archivo tambien se buscan en el inventario
    vendedores = cargar_vendedores(datos_ventas)
    if not vendedores:
        vendedores = cargar_vendedores(datos_inventario)

    ventas, descartados = cargar_ventas(datos_ventas)
    if len(descartados) > 0:
        print("Aviso: se ignoraron " + str(len(descartados))
              + " elemento(s) del archivo de ventas que no eran ventas.")

    print("Ventas encontradas: " + str(len(ventas)))
    separador = preguntar_separador()
    campo, orden = preguntar_orden()

    stock = {}
    for id_producto in productos:
        stock[id_producto] = productos[id_producto]["stock"]

    validas, rechazadas, stock_final = procesar_ventas(ventas, vendedores, productos, stock)

    salidas = os.path.join(carpeta, CARPETA_SALIDAS)
    if not os.path.isdir(salidas):
        os.makedirs(salidas)

    # un csv por cada vendedor activo
    grupos = agrupar_por_vendedor(validas)
    for id_vendedor in sorted(vendedores):
        if not vendedores[id_vendedor]["activo"]:
            continue
        propias = ordenar_ventas(grupos.get(id_vendedor, []), campo, orden)
        escribir_csv(os.path.join(salidas, "ventas_" + str(id_vendedor) + ".csv"),
                     COLUMNAS_VENTAS, [filas_de_venta(v) for v in propias], separador)

    escribir_csv(os.path.join(salidas, "ventas_rechazadas.csv"), COLUMNAS_RECHAZADAS,
                 [fila_rechazada(v) for v in rechazadas], separador)
    escribir_csv(os.path.join(salidas, "resumen_vendedores.csv"), COLUMNAS_RESUMEN,
                 filas_resumen(vendedores, validas), separador)
    escribir_inventario(os.path.join(salidas, "inventario_actualizado.json"),
                        actualizar_inventario(datos_inventario, stock_final))

    print("")
    print("Ventas validas: " + str(len(validas)) + "   rechazadas: " + str(len(rechazadas)))

    print("")
    print("Motivos de rechazo:")
    for venta in rechazadas:
        print("   " + str(venta["id_venta"]) + " (" + str(venta["id_vendedor"])
              + "): " + venta["motivo"])
    if not rechazadas:
        print("   ninguna")

    print("")
    print("Totales por vendedor:")
    for fila in filas_resumen(vendedores, validas):
        print("   " + str(fila["id_vendedor"]) + "  " + fila["nombre"]
              + "  " + str(fila["cantidad_ventas"]) + " venta(s), "
              + str(fila["unidades_vendidas"]) + " unidad(es), "
              + fila["total_vendido"])

    print("")
    print("Stock que queda:")
    for id_producto in sorted(productos):
        print("   " + str(id_producto) + ") " + productos[id_producto]["nombre"]
              + ": " + str(stock_final[id_producto]))

    total = 0
    for venta in validas:
        total += venta["total"]
    print("")
    print("Total vendido: " + formatear_monto(round(total, 2)))
    print("Se guardaron los archivos en " + salidas)


def main():
    carpeta = os.path.dirname(os.path.abspath(__file__))

    if "--pruebas" in sys.argv:
        import pruebas
        pruebas.ejecutar()
        return 0

    try:
        ejecutar(carpeta)
    except ErrorArchivo as problema:
        print("No se pudo terminar: " + str(problema))
    except KeyboardInterrupt:
        print("")
        print("Se cancelo la ejecucion.")
    except OSError as problema:
        print("Problema con los archivos: " + str(problema))

    return 0


if __name__ == "__main__":
    sys.exit(main())
