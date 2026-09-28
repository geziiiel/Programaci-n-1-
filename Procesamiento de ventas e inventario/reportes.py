import csv
import json

from calculos import formatear_monto

COLUMNAS_VENTAS = ["id_venta", "fecha", "cantidad_productos", "unidades", "subtotal",
                   "porcentaje_descuento", "descuento", "total"]
COLUMNAS_RECHAZADAS = ["id_venta", "fecha", "id_vendedor", "motivo"]
COLUMNAS_RESUMEN = ["id_vendedor", "nombre", "cantidad_ventas", "unidades_vendidas",
                    "total_vendido"]


def escribir_csv(ruta, columnas, filas, separador):
    try:
        with open(ruta, "w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=columnas,
                                      delimiter=separador, lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(filas)
    except OSError as problema:
        print("No se pudo escribir " + ruta + ": " + str(problema))


def escribir_inventario(ruta, inventario):
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(inventario, archivo, indent=2, ensure_ascii=False)
            archivo.write("\n")
    except OSError as problema:
        print("No se pudo escribir " + ruta + ": " + str(problema))


def filas_de_venta(venta):
    return {
        "id_venta": venta["id_venta"],
        "fecha": venta["fecha"],
        "cantidad_productos": venta["cantidad_productos"],
        "unidades": venta["unidades"],
        "subtotal": formatear_monto(venta["subtotal"]),
        "porcentaje_descuento": venta["porcentaje_descuento"],
        "descuento": formatear_monto(venta["descuento"]),
        "total": formatear_monto(venta["total"]),
    }


def fila_rechazada(rechazada):
    return {
        "id_venta": rechazada["id_venta"],
        "fecha": rechazada["fecha"],
        "id_vendedor": rechazada["id_vendedor"],
        "motivo": rechazada["motivo"],
    }


def agrupar_por_vendedor(ventas):
    """id_vendedor -> lista con las ventas de ese vendedor."""
    grupos = {}
    for venta in ventas:
        if venta["id_vendedor"] not in grupos:
            grupos[venta["id_vendedor"]] = []
        grupos[venta["id_vendedor"]].append(venta)
    return grupos


def filas_resumen(vendedores, ventas):
    """Un renglon por cada vendedor activo, tenga ventas o no."""
    grupos = agrupar_por_vendedor(ventas)
    filas = []
    for id_vendedor in sorted(vendedores):
        vendedor = vendedores[id_vendedor]
        if not vendedor["activo"]:
            continue
        propias = grupos.get(id_vendedor, [])
        filas.append({
            "id_vendedor": vendedor["id_vendedor"],
            "nombre": vendedor["nombre"],
            "cantidad_ventas": len(propias),
            "unidades_vendidas": sum(venta["unidades"] for venta in propias),
            "total_vendido": formatear_monto(round(sum(venta["total"] for venta in propias), 2)),
        })
    return filas
