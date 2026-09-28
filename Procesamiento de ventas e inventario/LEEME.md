# Procesamiento de ventas e inventario

Practica en Python. Lee `inventario.json` y `ventas.json`, mira que ventas estan
bien, descuenta el stock de las que sirven y escribe los CSV.

No hay que instalar nada, se usa solo la libreria estandar (json, csv, os, sys).

## Como se corre

```cmd
cd "C:\Users\Geziel\Desktop\Procesamiento de ventas e inventario"
python main.py
```

Primero pregunta con que separador se escriben los CSV (coma o punto y coma) y
luego como se ordenan las ventas de cada vendedor (por fecha, por total o por id
de venta, ascendente o descendente). Si se aprieta Enter sin escribir nada se usa
la coma y el orden por fecha de menor a mayor.

Las pruebas sueltas se corren con:

```cmd
python pruebas.py
```

o con `python main.py --pruebas`, que hace lo mismo.

## Los archivos

- `main.py` - lee los json, hace las preguntas, procesa y muestra lo que paso
- `datos.py` - leer los json, limpiar textos y convertir "25000.50" en numero
- `validaciones.py` - que motivo tiene cada venta para ser rechazada
- `calculos.py` - subtotal, descuento, total
- `ordenamiento.py` - el orden de las ventas (merge sort con recursion)
- `procesamiento.py` - recorre las ventas en orden y descuenta el stock
- `reportes.py` - escribe los csv y el json final
- `pruebas.py` - las pruebas con assert

## Que se rechaza

Una venta se tira entera (y no toca el stock) si:

- el id de venta ya se uso
- el vendedor no existe o esta inactivo
- la lista de items viene vacia
- algun producto no existe o esta inactivo
- el mismo producto aparece dos veces en la misma venta
- la cantidad esta vacia, no es numero, tiene decimales, es cero o es negativa
- no hay stock suficiente

El motivo va a `ventas_rechazadas.csv`.

Los descuentos: menos de $100.000 no hay descuento, de $100.000 a menos de
$300.000 es el 5%, y de $300.000 para arriba el 10%.

## Datos raros que hay que arreglar

En los archivos viene todo un poco sucio a proposito, y el programa lo normaliza:
precios y stock como texto (`"650000"`, `"15"`), nombres con espacios de sobra
(`"  Notebook basica  "`), el id de vendedor o de venta como texto, y fechas en
`DD/MM/AAAA` que quedan como `AAAA-MM-DD`. Las ventas vienen metidas en listas
dentro de listas, y eso se resuelve con recursion (`aplanar_ventas`).

## Lo que sale

Todo en la carpeta `salidas\`:

- `ventas_101.csv`, `ventas_202.csv` (tambien para el vendedor activo que no
  tenga ventas, sale solo con el encabezado)
- `ventas_rechazadas.csv`
- `resumen_vendedores.csv`
- `inventario_actualizado.json` (copia del original con el stock nuevo, para no
  perder `fecha_actualizacion` ni las categorias)

Los json de entrada no se modifican, el stock se descuenta sobre una copia.

## Con el ejemplo que dio el profesor

De las 14 ventas quedan 4 validas (1001, 1002, 1003 y 1011) y 10 rechazadas, y
cada rechazo cae en un motivo distinto. Los tres motivos que no salen en el
ejemplo (vendedor inexistente, cantidad en cero y cantidad no numerica) se prueban
en `pruebas.py`.
