from flask import Flask, request, send_file
from generar_factura import generar_factura_directa
from datetime import datetime
import re

app = Flask(__name__)

@app.route("/generar_desde_texto", methods=["POST"])
def generar_desde_texto():
    mensaje = request.form.get("mensaje")
    if not mensaje:
        return "No se recibió el texto", 400

    try:
        tokens = mensaje.strip().split()
        cliente = ""
        estado = ""
        fecha = ""
        productos = []

        cantidad_map = {
            "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
            "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
            "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
            "dieciséis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
            "veinte": 20, "veintiuno": 21, "veintidós": 22, "veintitrés": 23,
            "veinticuatro": 24, "veinticinco": 25, "veintiséis": 26, "veintisiete": 27,
            "veintiocho": 28, "veintinueve": 29, "treinta": 30, "treinta y uno": 31,
            "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70,
            "ochenta": 80, "noventa": 90, "cien": 100
        }

        i = 0
        while i < len(tokens):
            token = tokens[i].lower()

            if token == "cliente":
                i += 1
                cliente_parts = []
                while i < len(tokens) and tokens[i].lower() not in ["estado", "fecha"]:
                    cliente_parts.append(tokens[i])
                    i += 1
                cliente = " ".join(cliente_parts)

            elif token == "estado":
                i += 1
                if i < len(tokens):
                    estado = tokens[i]
                    i += 1

            elif token == "fecha":
                i += 1
                if i < len(tokens):
                    fecha = tokens[i]
                    i += 1

            elif re.match(r"^\d+$", token) or token in cantidad_map:
                # Es un producto
                if re.match(r"^\d+$", token):
                    cantidad = int(token)
                else:
                    cantidad = cantidad_map.get(token, 1)

                i += 1
                desc_parts = []
                while i < len(tokens) and tokens[i].lower() != "a":
                    desc_parts.append(tokens[i])
                    i += 1

                i += 1  # saltar "a"
                if i < len(tokens):
                    try:
                        precio = float(tokens[i])
                    except:
                        precio = 0
                    i += 1
                else:
                    precio = 0

                descripcion = " ".join(desc_parts)
                total = cantidad * precio
                productos.append([cantidad, descripcion, precio, total])

            else:
                i += 1

        if not productos:
            return "No se encontraron productos válidos.", 400

        # Ordenar productos alfabéticamente por descripción
        productos.sort(key=lambda x: x[1].lower())

        fecha_valida = procesar_fecha(fecha)

        pdf_stream = generar_factura_directa(cliente, estado, fecha_valida, productos)

        return send_file(
            pdf_stream,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Factura_{cliente}_{fecha_valida.replace('/', '-')}.pdf"
        )

    except Exception as e:
        return f"❌ Error al procesar el mensaje: {e}", 500

def procesar_fecha(fecha_str):
    if fecha_str.lower() == "hoy":
        return datetime.today().strftime("%d/%m/%Y")
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%d/%m/%Y")
    except:
        return datetime.today().strftime("%d/%m/%Y")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
