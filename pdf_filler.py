import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
import io
from datetime import datetime

def fill_pdf(input_path, output_path, data):
    # Ensure current_date is in the data, use provided or current date
    if 'current_date' not in data or not data['current_date']:
        data['current_date'] = datetime.now().strftime("%d/%m/%Y")

    # A4 size in points (595.27, 841.89)
    page_positions = {
        0: {
            'day': (426, 708),
            'monthx': (72, 694),
            'year': (250, 694),
            'company_address': (166, 656),
            'employee_name': (155, 593),
            'employee_address': (168, 580)
        },
        1: {
            'company_rep_name': (104, 95),  # Moved down further
            'designation': (130, 80)        # Moved down further
        },
        2: {
            'company_signature': (120, 745, True),
            'company_date': (98, 732),
            'employee_name': (104, 694),
            'employee_address': (114, 681),
            'employee_signature': (120, 668, True),
            'employee_date': (98, 655),
            'witness_name': (104, 616),
            'witness_signature': (120, 603, True),
            'witness_date': (98, 590)
        }
    }

    pdf = pdfplumber.open(input_path)
    output = PdfWriter()

    for page_num, page in enumerate(pdf.pages):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(595.27, 841.89))  # A4 size
        
        if page_num in page_positions:
            for field, pos in page_positions[page_num].items():
                if isinstance(pos, tuple) and len(pos) == 3:
                    x, y, bold = pos
                else:
                    x, y = pos
                    bold = False

                if 'date' in field.lower():
                    value = data.get('current_date', '')


                else:
                    value = data.get(field, '')

                if value:
                    if bold:
                        c.setFont('Times-Bold', 10)
                    else:
                        c.setFont('Times-Roman', 10)
                    c.drawString(x, y, str(value))

        c.save()
        packet.seek(0)

        new_pdf = PdfReader(packet)
        page = PdfReader(input_path).pages[page_num]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

    with open(output_path, 'wb') as outfile:
        output.write(outfile)

    pdf.close()