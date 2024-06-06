from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesize import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io, datetime

def generate_certificate(name):
    
    data = datetime.now().strftime("%d/%m/%Y")
    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=letter)
    height, width = letter

    template = ImageReader('static/images/template_certificate.png')
    c.drawImage(template, 0, 0, width=width, height=height)

    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0, 0, 0,)
    c.drawString(400, 200, name)

    c.setFont("Helvetica", 18)
    c.drawString(300, 100, f"Data de emissão: {data}")

    c.showPage()
    c.save()

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, mimetype='application/pdf', attachment_filename=f"Certificado Mestre Ágil - {name}.pdf")