from datetime import datetime

from datos import FORMATOS_FECHA


def fecha_comparable(texto):
    """Convierte la fecha a datetime para poder ordenarla bien.

    Si la fecha no se reconoce devuelve datetime.min, que queda siempre antes
    que cualquier fecha real, y asi no se rompe la comparacion.
    """
    for formato in FORMATOS_FECHA:
        try:
            return datetime.strptime(texto, formato)
        except (ValueError, TypeError):
            continue
    return datetime.min


def clave(venta, campo):
    """Valor por el que se compara una venta, del mismo tipo en todas."""
    if campo == "total":
        return venta["total"]
    if campo == "id_venta":
        # el id siempre llega como int en las ventas aceptadas
        return venta["id_venta"] if venta["id_venta"] is not None else 0
    return fecha_comparable(venta["fecha"])


def comparar(izquierda, derecha, campo):
    valor_izquierda = clave(izquierda, campo)
    valor_derecha = clave(derecha, campo)
    if valor_izquierda == valor_derecha:
        return 0
    return -1 if valor_izquierda < valor_derecha else 1


def mezclar(izquierda, derecha, campo):
    resultado = []
    i = 0
    j = 0
    while i < len(izquierda) and j < len(derecha):
        if comparar(izquierda[i], derecha[j], campo) <= 0:
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1
    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado


def ordenar_ascendente(ventas, campo):
    """Merge sort recursivo, siempre de menor a mayor."""
    if len(ventas) < 2:
        return list(ventas)

    medio = len(ventas) // 2
    izquierda = ordenar_ascendente(ventas[:medio], campo)
    derecha = ordenar_ascendente(ventas[medio:], campo)
    return mezclar(izquierda, derecha, campo)


def ordenar_ventas(ventas, campo="fecha", orden="asc"):
    """Ordena la lista de ventas por el campo pedido."""
    resultado = ordenar_ascendente(ventas, campo)

    # el merge sort siempre sale de menor a mayor, para el orden inverso se
    # invierte la lista al final
    if orden == "desc":
        resultado.reverse()
    return resultado
