from datos import a_entero, a_numero, limpiar, normalizar_fecha, normalizar_id, obtener


def normalizar_venta(venta):
    """Deja la venta con numeros enteros y los espacios ya fuera."""
    items = []
    for item in venta.get("items", []):
        if not isinstance(item, dict):
            items.append({"id_producto": None, "cantidad": None, "cantidad_cruda": item})
            continue
        cantidad = item.get("cantidad")
        items.append({
            "id_producto": normalizar_id(obtener(item, ("id_producto", "id"))),
            "cantidad": a_entero(cantidad),
            "cantidad_cruda": cantidad,
        })

    return {
        "id_venta": normalizar_id(venta.get("id_venta")),
        "fecha": normalizar_fecha(venta.get("fecha")),
        "id_vendedor": normalizar_id(venta.get("id_vendedor")),
        "items": items,
    }


def motivo_rechazo(venta, vendedores, productos, ids_vistos, stock):
    """Devuelve el motivo del rechazo o None si la venta esta buena.

    Se devuelve solo el primer problema, en el orden que pide la consigna, para
    que el motivo del CSV se entienda de una.
    """
    if venta["id_venta"] is None:
        return "ID de venta vacio"
    if venta["id_venta"] in ids_vistos:
        return "ID de venta repetido (" + str(venta["id_venta"]) + ")"

    id_vendedor = venta["id_vendedor"]
    if id_vendedor is None or id_vendedor not in vendedores:
        return "Vendedor inexistente (" + str(venta["id_vendedor"]) + ")"
    if not vendedores[id_vendedor]["activo"]:
        return "Vendedor inactivo (" + str(id_vendedor) + ")"

    items = venta["items"]
    if not items:
        return "Lista de productos vacia"

    vistos = set()
    for item in items:
        id_producto = item["id_producto"]
        if id_producto is None or id_producto not in productos:
            return "Producto inexistente (" + str(id_producto) + ")"
        if not productos[id_producto]["activo"]:
            return "Producto inactivo (" + str(id_producto) + ")"
        if id_producto in vistos:
            return "Producto repetido en la venta (" + str(id_producto) + ")"
        vistos.add(id_producto)

    for item in items:
        cantidad = item["cantidad"]
        if cantidad is None:
            # todavia no se sabe si es un problema de formato o que es decimal
            if a_numero(item["cantidad_cruda"]) is None:
                if item["cantidad_cruda"] is None or limpiar(item["cantidad_cruda"]) == "":
                    return "Cantidad vacia"
                return "Cantidad no numerica (" + str(item["cantidad_cruda"]) + ")"
            return "Cantidad decimal (" + str(item["cantidad_cruda"]) + ")"
        if cantidad == 0:
            return "Cantidad igual a cero"
        if cantidad < 0:
            return "Cantidad negativa (" + str(cantidad) + ")"

        if cantidad > stock[item["id_producto"]]:
            return ("Stock insuficiente (producto " + str(item["id_producto"])
                    + ": hay " + str(stock[item["id_producto"]])
                    + ", se piden " + str(cantidad) + ")")

    return None
