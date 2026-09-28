LIMITE_5 = 100000
LIMITE_10 = 300000


def calcular_subtotal(venta, productos):
    """Suma precio por cantidad de cada item de la venta."""
    total = 0
    for item in venta["items"]:
        total += productos[item["id_producto"]]["precio"] * item["cantidad"]
    return round(total, 2)


def porcentaje_descuento(subtotal):
    if subtotal >= LIMITE_10:
        return 10
    if subtotal >= LIMITE_5:
        return 5
    return 0


def calcular_descuento(subtotal, porcentaje):
    return round(subtotal * porcentaje / 100, 2)


def calcular_total(subtotal, descuento):
    return round(subtotal - descuento, 2)


def unidades(venta):
    suma = 0
    for item in venta["items"]:
        suma += item["cantidad"]
    return suma


def formatear_monto(valor):
    return "{:.2f}".format(valor)
