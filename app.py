from flask import Flask, request, send_file
from generar_factura import generar_factura_directa
from datetime import datetime
import re
import os

app = Flask(__name__)

@app.route("/generar_desde_texto", methods=["POST"])
def generar_desde_texto():
    mensaje = request.form.get("mensaje")
    if not mensaje:
        return "❌ No se recibió el texto.", 400

    try:
        lineas = mensaje.strip().splitlines()
        cliente = estado = fecha = ""
        productos = []
        errores = []

        for linea in lineas:
            if "Cliente:" in linea:
                cliente = linea.split(":", 1)[1].strip()
            elif "Estado:" in linea:
                estado = linea.split(":", 1)[1].strip()
            elif "Fecha:" in linea:
                fecha = linea.split(":", 1)[1].strip()
            elif "x" in linea and "a" in linea:
                match = re.match(r"(\d+)\s*x\s*(.*?)\s*a\s*([\d.]+)", linea)
                if match:
                    cantidad = int(match.group(1))
                    descripcion = match.group(2).strip()
                    precio = float(match.group(3))
                    total = cantidad * precio
                    productos.append([cantidad, descripcion, precio, total])
                else:
                    errores.append(f"❌ Formato incorrecto en línea: '{linea}'")

        # Validaciones
        if not cliente:
            errores.append("❌ Falta el campo 'Cliente'.")
        if not estado:
            errores.append("❌ Falta el campo 'Estado'.")
        if not fecha:
            errores.append("❌ Falta el campo 'Fecha'.")
        if not productos:
            errores.append("❌ No se encontraron productos válidos.")

        if errores:
            return "\n".join(errores), 400

        fecha_valida = validar_fecha(fecha)
        pdf_path = generar_factura_directa(cliente, estado, fecha_valida, productos)

        # Descargar con nombre personalizado
        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=os.path.basename(pdf_path)
        )

    except Exception as e:
        return f"❌ Error interno: {e}", 500

def validar_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%d/%m/%Y")
    except:
        return datetime.today().strftime("%d/%m/%Y")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
