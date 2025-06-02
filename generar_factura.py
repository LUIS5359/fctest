import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime
import re

def capitalizar(texto):
    return texto[0].upper() + texto[1:] if texto else texto

def generar_factura_directa(cliente, estado, fecha, productos):
    carpeta_facturas = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FACTURAS")
    os.makedirs(carpeta_facturas, exist_ok=True)

    direccion = "0Av Zona 2, San Francisco El Alto a 150 mts. del entronque"
    telefono = "3256-6671 o 3738-5499"
    logo_path = "logo.png"

    cliente_limpio = re.sub(r'[^a-zA-Z0-9]', '_', cliente.strip())
    fecha_formateada = fecha.replace("/", "-")
    nombre_base = f"FKMS_{cliente_limpio}_{fecha_formateada}"
    nombre_pdf = os.path.join("facturas", f"{nombre_base}.pdf")


    contador = 1
    while os.path.exists(nombre_pdf):
        nombre_pdf = os.path.join(carpeta_facturas, f"{nombre_base}_{contador}.pdf")
        contador += 1

    c = canvas.Canvas(nombre_pdf, pagesize=letter)

    try:
        logo = ImageReader(logo_path)
        c.drawImage(logo, 40, 720, width=80, height=80)
    except:
        print("⚠️ Logo no encontrado, se generará sin él.")

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#003366"))
    c.drawString(150, 770, "Kim's Sports")
    c.setFillColor(colors.black)

    c.setFont("Helvetica", 10)
    c.drawString(150, 750, f"Dirección: {direccion}")
    c.drawString(150, 735, f"Teléfono: {telefono}")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(50, 700, f"FECHA: {fecha}")
    c.drawString(50, 685, f"CLIENTE: {cliente}")
    c.drawString(50, 670, f"ESTADO: {estado}")
    c.setFillColor(colors.black)

    y = 640
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#003366"))
    c.drawString(50, y, "Descripción")
    c.drawString(250, y, "Cantidad")
    c.drawString(350, y, "Precio")
    c.drawString(450, y, "Total")
    c.line(50, y - 5, 500, y - 5)

    y -= 20
    c.setFont("Helvetica", 10)
    total_factura = 0

    for cantidad, descripcion, precio, total in productos:
        if y < 100:
            c.showPage()
            y = 750

        c.drawString(50, y, capitalizar(descripcion[:40]))
        c.drawString(250, y, str(cantidad))
        c.drawString(350, y, f"Q {precio:.2f}")
        c.drawString(450, y, f"Q {total:.2f}")
        total_factura += total
        c.setStrokeColor(colors.lightgrey)
        c.line(50, y - 5, 500, y - 5)
        y -= 18

    if y < 100:
        c.showPage()
        y = 750

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#003366"))
    c.drawString(350, y - 10, "TOTAL:")
    c.drawString(450, y - 10, f"Q {total_factura:,.2f}")
    c.line(350, y - 15, 500, y - 15)

    c.setFont("Times-Italic", 11)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(50, y - 50, "(Factura no contable con fines informativos.)")
    c.drawString(50, y - 65, "¡Gracias por su compra, vuelva pronto!")

    c.save()
    return nombre_pdf
