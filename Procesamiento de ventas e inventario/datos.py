import copy
import json
import math
from datetime import datetime


class ErrorArchivo(Exception):
    """Se lanza cuando un JSON no se puede leer o esta mal formado."""


FORMATOS_FECHA = ("%Y-%m-%d", "%d/%m/%Y")


def leer_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        raise ErrorArchivo("No se encontro el archivo " + ruta)
    except json.JSONDecodeError as problema:
        raise ErrorArchivo("El archivo " + ruta + " no es un JSON valido (linea "
                           + str(problema.lineno) + ")")
    except OSError as problema:
        raise ErrorArchivo("No se pudo leer " + ruta + ": " + str(problema))


def obtener(dato, nombres):
    # el enunciado no aclara como se llaman los campos del producto, entonces
    # se prueba con los dos nombres que se usan
    for nombre in nombres:
        if nombre in dato:
            return dato[nombre]
    return None


def limpiar(texto):
    """Quita espacios de sobra, tambien los del medio."""
    if texto is None:
        return ""
    return " ".join(str(texto).split())


def a_numero(valor):
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        numero = float(valor)
    elif isinstance(valor, str):
        numero = a_numero_texto(valor)
    else:
        return None

    if numero is None or not math.isfinite(numero):
        return None
    return numero


def a_numero_texto(valor):
    texto = valor.strip().replace(" ", "")
    if texto == "":
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def a_entero(valor):
    """Devuelve None si el numero no es entero, por ejemplo 2.5."""
    numero = a_numero(valor)
    if numero is None or numero != int(numero):
        return None
    return int(numero)


def normalizar_id(valor):
    return a_entero(valor)


def normalizar_fecha(valor):
    texto = limpiar(valor)
    if texto == "":
        return ""
    for formato in FORMATOS_FECHA:
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return texto


def aplanar_ventas(dato, ventas, descartados):
    """Baja con recursion hasta encontrar las ventas.

    En el archivo hay listas dentro de listas y tambien diccionarios que solo
    sirven para agrupar, asi que no se puede leer con un for simple.
    """
    if isinstance(dato, dict):
        if "id_venta" in dato or "id_vendedor" in dato or "items" in dato:
            ventas.append(dato)
        else:
            for valor in dato.values():
                aplanar_ventas(valor, ventas, descartados)
    elif isinstance(dato, list):
        for valor in dato:
            aplanar_ventas(valor, ventas, descartados)
    else:
        descartados.append(dato)


def cargar_ventas(datos):
    ventas = []
    descartados = []
    if isinstance(datos, dict) and "ventas" in datos:
        aplanar_ventas(datos["ventas"], ventas, descartados)
    else:
        aplanar_ventas(datos, ventas, descartados)
    return ventas, descartados


def cargar_vendedores(datos):
    vendedores = {}
    if not isinstance(datos, dict):
        return vendedores

    for dato in datos.get("vendedores", []):
        id_vendedor = normalizar_id(obtener(dato, ("id", "id_vendedor")))
        if id_vendedor is None:
            continue
        activo = dato.get("activo", True)
        vendedores[id_vendedor] = {
            "id_vendedor": id_vendedor,
            "nombre": limpiar(dato.get("nombre")),
            "activo": True if activo is None else bool(activo),
        }
    return vendedores


def cargar_productos(datos):
    productos = {}
    if not isinstance(datos, dict):
        return productos

    for dato in datos.get("productos", []):
        id_producto = normalizar_id(obtener(dato, ("id", "id_producto")))
        if id_producto is None:
            continue
        precio = a_numero(obtener(dato, ("precio", "precio_unitario")))
        stock = a_numero(dato.get("stock"))
        activo = dato.get("activo", True)
        productos[id_producto] = {
            "id_producto": id_producto,
            "nombre": limpiar(dato.get("nombre")),
            "precio": precio if precio is not None else 0.0,
            "stock": int(stock) if stock is not None else 0,
            "activo": True if activo is None else bool(activo),
        }
    return productos


def actualizar_inventario(datos, stock):
    """Copia el inventario y le cambia solo el stock a cada producto.

    Se copia completo para no perder lo que el programa no usa, como
    fecha_actualizacion o la categoria.
    """
    copia = copy.deepcopy(datos)
    for producto in copia.get("productos", []):
        id_producto = normalizar_id(obtener(producto, ("id", "id_producto")))
        if id_producto in stock:
            producto["stock"] = stock[id_producto]
    return copia
