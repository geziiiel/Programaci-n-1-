from calculos import (
    calcular_descuento,
    calcular_subtotal,
    calcular_total,
    porcentaje_descuento,
    unidades,
)
from validaciones import motivo_rechazo, normalizar_venta


def procesar_ventas(ventas, vendedores, productos, stock):
    """Recorre las ventas en el orden del archivo y separa validas de rechazadas.

    Devuelve (validas, rechazadas, stock_final). El stock es una copia, asi que
    el diccionario que recibe el programa no se toca.
    """
    validas = []
    rechazadas = []
    ids_vistos = set()
    stock_disponible = dict(stock)

    for venta in ventas:
        limpia = normalizar_venta(venta)
        motivo = motivo_rechazo(limpia, vendedores, productos, ids_vistos, stock_disponible)

        if motivo is not None:
            # una venta rechazada no toca el inventario
            rechazadas.append({
                "id_venta": limpia["id_venta"] if limpia["id_venta"] is not None
                else venta.get("id_venta", ""),
                "fecha": limpia["fecha"],
                "id_vendedor": limpia["id_vendedor"] if limpia["id_vendedor"] is not None
                else venta.get("id_vendedor", ""),
                "motivo": motivo,
            })
            continue

        subtotal = calcular_subtotal(limpia, productos)
        porcentaje = porcentaje_descuento(subtotal)
        descuento = calcular_descuento(subtotal, porcentaje)
        total = calcular_total(subtotal, descuento)

        for item in limpia["items"]:
            stock_disponible[item["id_producto"]] -= item["cantidad"]

        validas.append({
            "id_venta": limpia["id_venta"],
            "fecha": limpia["fecha"],
            "id_vendedor": limpia["id_vendedor"],
            "items": limpia["items"],
            "cantidad_productos": len(limpia["items"]),
            "unidades": unidades(limpia),
            "subtotal": subtotal,
            "porcentaje_descuento": porcentaje,
            "descuento": descuento,
            "total": total,
        })
        ids_vistos.add(limpia["id_venta"])

    return validas, rechazadas, stock_disponible
