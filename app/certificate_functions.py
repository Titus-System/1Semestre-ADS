
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from datetime import date as current_time
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from os.path import abspath, dirname, join

def create_certificate(student_name):
    
    script_dir = dirname(abspath(__file__))
    image_path = "static/images/template_certificate.jpeg"
    background_image_path = join(script_dir, image_path)
    date = current_time.today()
    output_path = "certificado.pdf"
    pdfmetrics.registerFont(TTFont('Gwendolyn-Bold', './static/fonts/Gwendolyn-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Datefont', './static/fonts/GentiumBookPlus-Bold.ttf'))
    
    # Carrega a imagem de fundo e obtém suas dimensões
    image = ImageReader(background_image_path)
    img_width, img_height = image.getSize()

    # Converte as dimensões da imagem de pixels para pontos (1 inch = 72 points)
    img_width_points = img_width * 72 / 72
    img_height_points = img_height * 72 / 72

    # Criação do canvas com as dimensões da imagem
    c = canvas.Canvas(output_path, pagesize=(img_width_points, img_height_points))

    # Adiciona a imagem de fundo
    c.drawImage(background_image_path, 0, 0, width=img_width_points, height=img_height_points)

    # Adicionar nome do aluno
    c.setFont('Gwendolyn-Bold', 80)
    c.setFillColor(colors.black)
    c.drawCentredString(img_width_points / 2.0, img_height_points - 5.7 * inch, student_name)

    # Adicionar data de conclusão
    date_x = img_width_points / 2.0 + 40
    date_y = (img_height_points - 7.95 * inch)  # Ajuste a altura conforme necessário
    c.setFont('Datefont', 26)
    c.setFillColor(HexColor('#08BDF3'))
    c.drawCentredString(date_x, date_y, str(date.today()))

    # Finalizar o PDF
    c.showPage()
    c.save()
