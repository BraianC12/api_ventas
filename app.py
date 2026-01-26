from flask import Flask, jsonify
import sqlite3
from flask import jsonify

app = Flask(__name__)
DB_PATH = "database/ventas.db"

def conectar_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return jsonify({"mensaje": "API de Ventas funcionando"})


@app.route("/ventas")
def obtener_ventas():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fecha, producto, categoria, cantidad, precio_unit
        FROM ventas
                   """)
    
    filas = cursor.fetchall()
    conn.close()

    ventas = []

    for fila in filas:
        ventas.append({
            "fecha" : fila["fecha"],
            "producto" : fila["producto"],
            "categoria" : fila["categoria"],
            "cantidad" : fila["cantidad"],
            "precio_unit" : fila["precio_unit"]
        })
    
    return jsonify(ventas)

#FILTRO
@app.route ("/ventas/categoria/<categoria>")
def ventas_por_categoria(categoria):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
            SELECT fecha, producto, categoria, cantidad, precio_unit
            FROM ventas
            WHERE LOWER(categoria) = LOWER(?)
    """, (categoria,))

    filas = cursor.fetchall()
    conn.close()

    #validacion de resultados

    if not filas:
        return jsonify({
            "mensaje": "No se encontraron ventas para la categoria solicitada"
        }), 404

    ventas = []
    for fila in filas:
        ventas.append({
            "fecha": fila["fecha"],
            "producto": fila["producto"],
            "categoria": fila["categoria"],
            "cantidad": fila["cantidad"],
            "precio_unit": fila["precio_unit"]
        })
    
    return jsonify(ventas)

#VENTAS TOTAL
@app.route ("/ventas/total")
def total_facturado():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
       SELECT SUM(cantidad * precio_unit) AS total
       FROM ventas
    """)

    resultado = cursor.fetchone()
    conn.close()

    total = resultado["total"]

    return jsonify({
        "total_facturado": total
    })


#METRICAS
@app.route("/metricas")
def obtener_metricas():
    conn = conectar_db()
    cursor = conn.cursor()

    #total facturado
    cursor.execute("""
        SELECT SUM (cantidad * precio_unit) AS total
        FROM ventas                   
        """)
    total_facturado = cursor.fetchone()["total"]

    #ticket promedio
    cursor.execute("""
        SELECT AVG(cantidad * precio_unit) AS promedio
        FROM ventas       
        """)
    ticket_promedio = cursor.fetchone()["promedio"]

    #cantidad de ventas
    cursor.execute("""
        SELECT COUNT(*) AS CANTIDAD
        FROM ventas
        """)
    cantidad_ventas = cursor.fetchone()["cantidad"]

    conn.close()

    return jsonify({
        "total_facturado": total_facturado,
        "ticket_promedio": ticket_promedio,
        "cantidad_ventas": cantidad_ventas
    })

#ventas por mes
@app.route("/metricas/por-mes")
def metricas_por_mes():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            strftime('%Y-%m', fecha) AS mes,
            SUM(cantidad * precio_unit) AS total_facturado
        FROM ventas
        GROUP BY mes
        ORDER BY mes
        """)
    
    resultados = cursor.fetchall()
    conn.close()

    respuesta = []

    for fila in resultados:
        respuesta.append({
            "mes": fila["mes"],
            "total_facturado": fila["total_facturado"]
        })

    return jsonify(respuesta)

if __name__ == "__main__":
    app.run(debug=True)