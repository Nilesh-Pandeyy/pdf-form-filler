
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

    page_positions = {
        0: {
            'day': (426.905595, 842 - 143.94677784452153),
            'monthx': (72.0, 842 - 157.17065446952154),  # Updated to use 'monthx'
            'year': (250.0, 842 - 157.17065446952154),  # Added year position
            'company_address': (166.42608225, 842 - 195.61841046952156),
            'employee_name': (155.331768, 842 - 259.2900438445215),
            'employee_address': (168.10511400000001, 842 - 272.5139204695215)
        },
        1: {
            'company_rep_name': (104.21888325, 842 - 732.6181604695215),
            'designation': (130.346409, 842 - 745.8420374695215)
        },
        2: {
            'company_signature': (120.345417, 842 - 81.4990238445215, True),
            'company_date': (98.66930024999999, 842 - 94.7229004695215),
            'employee_name': (104.21888325, 842 - 133.17065446952154),
            'employee_address': (114.224739, 842 - 146.39453146952155),
            'employee_signature': (120.345417, 842 - 159.61840846952157, True),
            'employee_date': (98.66930024999999, 842 - 172.84228546952147),
            'witness_name': (104.21888325, 842 - 211.2900404695215),
            'witness_signature': (120.345417, 842 - 224.51391746952152, True),
            'witness_date': (98.66930024999999, 842 - 237.73779446952142)
        }
    }

    pdf = pdfplumber.open(input_path)
    output = PdfWriter()

    for page_num, page in enumerate(pdf.pages):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(612, 842))

        if page_num in page_positions:
            for field, pos in page_positions[page_num].items():
                if isinstance(pos, tuple) and len(pos) == 3:
                    x, y, bold = pos
                else:
                    x, y = pos
                    bold = False

                if 'date' in field.lower():
                    value = data.get('current_date', '')
                elif field == 'company_signature':
                    value = data.get('company_rep_name', '')
                elif field == 'witness_signature':
                    value = data.get('witness_name', '')
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