"""
API REST de Inventario (Flask + PostgreSQL).

La configuración se lee de VARIABLES DE ENTORNO, así el mismo código
funciona en tu computador, en un contenedor o en un servidor sin cambiarlo.

Variables:
    DB_HOST      host de la base de datos        (por defecto: localhost)
    DB_PORT      puerto de la base de datos      (por defecto: 5432)
    DB_NAME      nombre de la base de datos      (por defecto: inventario)
    DB_USER      usuario                         (por defecto: inventario_user)
    DB_PASSWORD  contraseña                      (por defecto: vacía)
"""
import os

import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.json.sort_keys = False
app.json.ensure_ascii = False

# Columnas que devuelve la API (precio como número y fecha en formato ISO)
COLUMNAS = ("id, nombre, precio::float AS precio, stock, "
            "to_char(creado_en, 'YYYY-MM-DD\"T\"HH24:MI:SS') AS creado_en")


def conectar():
    """Abre una conexión nueva con la base de datos."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "inventario"),
        user=os.getenv("DB_USER", "inventario_user"),
        password=os.getenv("DB_PASSWORD", ""),
        connect_timeout=3,
    )


def ejecutar(sql, params=None, uno=False):
    """Ejecuta una consulta y devuelve las filas (o una sola fila si uno=True)."""
    conexion = conectar()
    try:
        with conexion:  # confirma (commit) si todo sale bien
            with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                if cursor.description is None:
                    return None
                return cursor.fetchone() if uno else cursor.fetchall()
    finally:
        conexion.close()


def validar_producto(datos):
    """Valida el cuerpo JSON. Devuelve (producto_limpio, mensaje_de_error)."""
    if not isinstance(datos, dict):
        return None, "El cuerpo debe ser un objeto JSON."
    nombre = str(datos.get("nombre", "")).strip()
    if not nombre:
        return None, "El campo 'nombre' es obligatorio."
    try:
        precio = float(datos.get("precio"))
        stock = int(datos.get("stock", 0))
    except (TypeError, ValueError):
        return None, "'precio' y 'stock' deben ser números."
    if precio < 0 or stock < 0:
        return None, "'precio' y 'stock' no pueden ser negativos."
    return {"nombre": nombre, "precio": precio, "stock": stock}, None


@app.errorhandler(psycopg2.OperationalError)
def base_de_datos_caida(_error):
    return jsonify(error="La base de datos no está disponible."), 503


@app.get("/")
def inicio():
    return jsonify(servicio="API de Inventario", version="1.0", documentacion="/productos")


@app.get("/health")
def health():
    """Usado por Docker (HEALTHCHECK) para saber si el servicio está sano."""
    try:
        ejecutar("SELECT 1")
        return jsonify(status="ok", db="up")
    except psycopg2.Error:
        return jsonify(status="error", db="down"), 503


@app.get("/productos")
def listar():
    return jsonify(ejecutar(f"SELECT {COLUMNAS} FROM productos ORDER BY id"))


@app.get("/productos/<int:id_producto>")
def obtener(id_producto):
    fila = ejecutar(f"SELECT {COLUMNAS} FROM productos WHERE id = %s", (id_producto,), uno=True)
    if fila is None:
        return jsonify(error="Producto no encontrado."), 404
    return jsonify(fila)


@app.post("/productos")
def crear():
    producto, error = validar_producto(request.get_json(silent=True))
    if error:
        return jsonify(error=error), 400
    fila = ejecutar(
        f"INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s) RETURNING {COLUMNAS}",
        (producto["nombre"], producto["precio"], producto["stock"]), uno=True)
    return jsonify(fila), 201

@app.get("/productos/buscar")
def buscar():
    texto = request.args.get("nombre", "").strip()
    filas = ejecutar(
        f"SELECT {COLUMNAS} FROM productos WHERE nombre ILIKE %s ORDER BY id",
        (f"%{texto}%",))
    return jsonify(filas)

@app.put("/productos/<int:id_producto>")
def actualizar(id_producto):
    producto, error = validar_producto(request.get_json(silent=True))
    if error:
        return jsonify(error=error), 400
    fila = ejecutar(
        f"UPDATE productos SET nombre = %s, precio = %s, stock = %s WHERE id = %s RETURNING {COLUMNAS}",
        (producto["nombre"], producto["precio"], producto["stock"], id_producto), uno=True)
    if fila is None:
        return jsonify(error="Producto no encontrado."), 404
    return jsonify(fila)


@app.delete("/productos/<int:id_producto>")
def eliminar(id_producto):
    fila = ejecutar("DELETE FROM productos WHERE id = %s RETURNING id", (id_producto,), uno=True)
    if fila is None:
        return jsonify(error="Producto no encontrado."), 404
    return jsonify(mensaje="Producto eliminado.", id=id_producto)


if __name__ == "__main__":
    # Solo para desarrollo local. En el contenedor se usa gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=True)
