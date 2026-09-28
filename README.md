# Programación 1

Practicas de la materia. Cada carpeta es una practica distinta.

## Procesamiento de ventas e inventario

Programa en Python que lee `inventario.json` y `ventas.json`, valida cada venta,
descuenta del stock las que estan bien y escribe los reportes en CSV.

```cmd
cd "Procesamiento de ventas e inventario"
python main.py
```

Al correrlo pregunta con que separador se escriben los CSV (coma o punto y coma)
y como se ordenan las ventas de cada vendedor (por fecha, por total o por id de
venta, ascendente o descendente). Los archivos se generan en la carpeta
`salidas\`.

El detalle esta en `Procesamiento de ventas e inventario/LEEME.md`.
