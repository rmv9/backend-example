import os

from django.shortcuts import render
from fpdf import FPDF

from recipes.constants import (
    NONE_MONTSERRAT_SIZE, B_MONTSERRAT_SIZE, I_MONTSERRAT_SIZE,
    CL_SET_FILL, CL_TXT, REC_PARAMS, CEL_PARAMS, IMAGE_PARAMS,
    Y_CRD, LINE_FEED, CL_FOOTER_TXT, FT_CELL_PARAMS,
    PDF_CELL_PARAMS, PDF_LINE_FEED, CL_BLACK

)
from foodgram.settings import BASE_DIR

FONTS_DIR = BASE_DIR / 'data/fonts'
LOGO = BASE_DIR / 'data/logo.png'


class PDF(FPDF):
    """
    Create pattern for PDF
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._set_font()

    def _set_font(self) -> None:
        self.add_font(
            'Montserrat',
            style='',
            fname=f'{FONTS_DIR}/Montserrat-Regular.ttf',
        )
        self.add_font(
            'Montserrat',
            style='B',
            fname=f'{FONTS_DIR}/Montserrat-Bold.ttf',
        )
        self.add_font(
            'Montserrat',
            style='I',
            fname=f'{FONTS_DIR}/Montserrat-Italic.ttf',
        )
        self.set_font('Montserrat')
        self.set_text_shaping(True)

    def header(self) -> None:
        self.set_font('Montserrat', 'B', size=B_MONTSERRAT_SIZE)
        self.set_text_color(
            CL_TXT['r'], CL_TXT['g'], CL_TXT['b']
        )
        self.set_fill_color(
            CL_SET_FILL['r'],  CL_SET_FILL['g'], CL_SET_FILL['b']
        )
        self.rect(
            REC_PARAMS['x'], REC_PARAMS['y'], REC_PARAMS['w'], REC_PARAMS['h'],
            style='F'
        )
        self.cell(
            CEL_PARAMS['w'], CEL_PARAMS['h'],
            'Список покупок', align='C'
        )
        self.image(
            LOGO, IMAGE_PARAMS['x'], IMAGE_PARAMS['y'], IMAGE_PARAMS['w']
        )
        self.ln(LINE_FEED)

    def footer(self) -> None:
        link = os.getenv('FOODGRAM_LINK')
        if link is None:
            return

        self.set_y(Y_CRD)
        self.set_text_color(CL_FOOTER_TXT)
        text_link = link.split('://', 1)[-1]
        self.cell(
            FT_CELL_PARAMS['w'], FT_CELL_PARAMS['h'],
            text_link, align='R', link=link
        )

    def get_pdf(self, html_text=None):
        if not self.page:
            self.add_page()
        if html_text is not None:
            self.write_html(html_text)

        return self.output()


def generate_pdf_file(ingredients, recipes, request):
    html = render(
        request,
        'purchase_product.html',
        {'ingredients': ingredients},
    ).content.decode('utf-8')
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Montserrat', 'I', size=I_MONTSERRAT_SIZE)
    pdf.set_text_color(
        CL_BLACK['r'], CL_BLACK['g'], CL_BLACK['b']
    )
    for recipe in recipes:
        pdf.cell(
            PDF_CELL_PARAMS['w'], PDF_CELL_PARAMS['h'],
            recipe, align='L', border='B', new_x='LEFT', new_y='NEXT'
        )
    pdf.ln(PDF_LINE_FEED)
    pdf.set_font('Montserrat', '', size=NONE_MONTSERRAT_SIZE)
    pdf_file = pdf.get_pdf(html)
    return pdf_file
