"""Pruebas con assert de las funciones que se pueden revisar solas.

Se pueden ejecutar de dos formas:

    python pruebas.py
    python main.py --pruebas
"""

import sys

from calculos import (calcular_descuento, calcular_subtotal, calcular_total,
                      porcentaje_descuento, unidades)
from datos import a_entero, a_numero, aplanar_ventas, limpiar, normalizar_fecha
from ordenamiento import ordenar_ventas
from procesamiento import procesar_ventas
from validaciones import motivo_rechazo, normalizar_venta

PRODUCTOS = {
    1: {"id_producto": 1, "nombre": "Teclado", "precio": 85000.0, "stock": 10, "activo": True},
    2: {"id_producto": 2, "nombre": "Mouse", "precio": 25000.5, "stock": 4, "activo": True},
    3: {"id_producto": 3, "nombre": "Impresora", "precio": 54000.0, "stock": 8, "activo": False},
}

VENDEDORES = {
    101: {"id_vendedor": 101, "nombre": "Ana", "activo": True},
    202: {"id_vendedor": 202, "nombre": "Carlos", "activo": True},
    303: {"id_vendedor": 303, "nombre": "Maria", "activo": False},
}

STOCK = {1: 10, 2: 4, 3: 8}


def prueba_limpiar():
    assert limpiar("  Notebook   basica  ") == "Notebook basica"
    assert limpiar("Mouse inalambrico") == "Mouse inalambrico"
    assert limpiar(None) == ""
    assert limpiar("") == ""


def prueba_conversion_numeros():
    assert a_numero("85000") == 85000.0
    assert a_numero(" 25000.50 ") == 25000.5
    assert a_numero("dos") is None
    assert a_numero("2,5") is None
    assert a_numero("") is None
    assert a_numero(True) is None

    assert a_entero("3") == 3
    assert a_entero(3.0) == 3
    assert a_entero("2.5") is None
    assert a_entero("-1") == -1


def prueba_normalizar_fecha():
    assert normalizar_fecha("2026-09-05") == "2026-09-05"
    assert normalizar_fecha("05/09/2026") == "2026-09-05"
    assert normalizar_fecha("  ") == ""
    assert normalizar_fecha("sin fecha") == "sin fecha"


def prueba_aplanar_ventas():
    ventas = []
    descartados = []
    dato = {
        "ventas": [
            {"id_venta": 1},
            [[{"id_venta": 2}]],
            {"lote": [{"id_venta": 3}]},
            "basura",
        ]
    }
    aplanar_ventas(dato, ventas, descartados)
    assert [venta["id_venta"] for venta in ventas] == [1, 2, 3]
    assert descartados == ["basura"]

    ventas = []
    descartados = []
    aplanar_ventas({"ventas": []}, ventas, descartados)
    assert ventas == [] and descartados == []


def prueba_porcentaje_descuento():
    assert porcentaje_descuento(0) == 0
    assert porcentaje_descuento(99999.99) == 0
    assert porcentaje_descuento(100000) == 5
    assert porcentaje_descuento(299999.99) == 5
    assert porcentaje_descuento(300000) == 10
    assert porcentaje_descuento(1000000) == 10


def prueba_calculo_montos():
    assert calcular_descuento(150000, 5) == 7500.0
    assert calcular_descuento(150000, 0) == 0.0
    assert calcular_total(150000, 7500) == 142500.0

    venta = {"items": [{"id_producto": 1, "cantidad": 2},
                       {"id_producto": 2, "cantidad": 2}]}
    assert calcular_subtotal(venta, PRODUCTOS) == 220001.0
    assert unidades(venta) == 4


def prueba_rechazos():
    repetida = normalizar_venta({"id_venta": 1, "id_vendedor": 101,
                                 "items": [{"id_producto": 1, "cantidad": 1}]})
    vendedor_fantasma = normalizar_venta({"id_venta": 2, "id_vendedor": 777,
                                          "items": [{"id_producto": 1, "cantidad": 1}]})
    assert "repetido" in motivo_rechazo(repetida, VENDEDORES, PRODUCTOS, {1}, STOCK)
    assert "inexistente" in motivo_rechazo(vendedor_fantasma, VENDEDORES, PRODUCTOS, set(), STOCK)

    inactivo = normalizar_venta({"id_venta": 3, "id_vendedor": 303,
                                 "items": [{"id_producto": 1, "cantidad": 1}]})
    assert "inactivo" in motivo_rechazo(inactivo, VENDEDORES, PRODUCTOS, set(), STOCK)

    sin_items = normalizar_venta({"id_venta": 4, "id_vendedor": 101, "items": []})
    assert "vacia" in motivo_rechazo(sin_items, VENDEDORES, PRODUCTOS, set(), STOCK)

    producto_malo = normalizar_venta({"id_venta": 5, "id_vendedor": 101,
                                      "items": [{"id_producto": 99, "cantidad": 1}]})
    producto_inactivo = normalizar_venta({"id_venta": 6, "id_vendedor": 101,
                                          "items": [{"id_producto": 3, "cantidad": 1}]})
    repetido = normalizar_venta({"id_venta": 7, "id_vendedor": 101, "items": [
        {"id_producto": 1, "cantidad": 1}, {"id_producto": 1, "cantidad": 2}]})
    assert "inexistente" in motivo_rechazo(producto_malo, VENDEDORES, PRODUCTOS, set(), STOCK)
    assert "inactivo" in motivo_rechazo(producto_inactivo, VENDEDORES, PRODUCTOS, set(), STOCK)
    assert "repetido" in motivo_rechazo(repetido, VENDEDORES, PRODUCTOS, set(), STOCK)

    for cantidad, esperado in (("", "vacia"), ("dos", "no numerica"), ("2.5", "decimal"),
                               (0, "cero"), (-2, "negativa")):
        venta = normalizar_venta({"id_venta": 8, "id_vendedor": 101, "items": [
            {"id_producto": 1, "cantidad": cantidad}]})
        motivo = motivo_rechazo(venta, VENDEDORES, PRODUCTOS, set(), STOCK)
        assert motivo is not None and esperado in motivo, (cantidad, motivo)

    sin_stock = normalizar_venta({"id_venta": 9, "id_vendedor": 101,
                                  "items": [{"id_producto": 2, "cantidad": 9}]})
    assert "Stock insuficiente" in motivo_rechazo(sin_stock, VENDEDORES, PRODUCTOS, set(), STOCK)

    buena = normalizar_venta({"id_venta": 10, "id_vendedor": "101",
                              "items": [{"id_producto": 1, "cantidad": "2"}]})
    assert motivo_rechazo(buena, VENDEDORES, PRODUCTOS, set(), STOCK) is None


def prueba_ordenar():
    ventas = [
        {"id_venta": 1003, "fecha": "2026-09-02", "total": 900.0},
        {"id_venta": 1001, "fecha": "2026-09-05", "total": 100.0},
        {"id_venta": 1002, "fecha": "2026-09-03", "total": 500.0},
    ]
    assert [v["id_venta"] for v in ordenar_ventas(ventas, "fecha", "asc")] == [1003, 1002, 1001]
    assert [v["id_venta"] for v in ordenar_ventas(ventas, "fecha", "desc")] == [1001, 1002, 1003]
    assert [v["id_venta"] for v in ordenar_ventas(ventas, "total", "asc")] == [1001, 1002, 1003]
    assert [v["id_venta"] for v in ordenar_ventas(ventas, "id_venta", "desc")] == [1003, 1002, 1001]
    assert ordenar_ventas([], "fecha", "asc") == []
    assert len(ordenar_ventas(ventas, "fecha", "asc")) == len(ventas)


def prueba_stock_no_se_toca():
    ventas = [
        {"id_venta": 1001, "fecha": "2026-09-01", "id_vendedor": 101,
         "items": [{"id_producto": 1, "cantidad": 2}]},
        {"id_venta": 1002, "fecha": "2026-09-02", "id_vendedor": 101,
         "items": [{"id_producto": 2, "cantidad": 99}]},
        {"id_venta": 1003, "fecha": "2026-09-03", "id_vendedor": 101,
         "items": [{"id_producto": 1, "cantidad": 1}]},
    ]
    original = dict(STOCK)

    validas, rechazadas, stock_final = procesar_ventas(ventas, VENDEDORES, PRODUCTOS, STOCK)

    assert len(validas) == 2
    assert len(rechazadas) == 1
    assert STOCK == original, "el diccionario original no se debe modificar"
    assert stock_final[1] == 7
    assert stock_final[2] == 4
    assert validas[0]["subtotal"] == 170000.0
    assert validas[0]["porcentaje_descuento"] == 5
    assert validas[0]["descuento"] == 8500.0
    assert validas[0]["total"] == 161500.0
    assert validas[0]["unidades"] == 2
    assert validas[0]["cantidad_productos"] == 1


def ejecutar():
    pruebas = [prueba_limpiar, prueba_conversion_numeros, prueba_normalizar_fecha,
               prueba_aplanar_ventas, prueba_porcentaje_descuento, prueba_calculo_montos,
               prueba_rechazos, prueba_ordenar, prueba_stock_no_se_toca]

    for prueba in pruebas:
        prueba()
        print("ok: " + prueba.__name__)

    print("")
    print("Las " + str(len(pruebas)) + " pruebas pasaron.")


if __name__ == "__main__":
    ejecutar()
