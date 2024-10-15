import os

from django.shortcuts import render
from fpdf import FPDF

from foodgram.settings import BASE_DIR


FONTS_DIR = BASE_DIR / 'data/fonts'
LOGO = BASE_DIR / 'data/logo.png'


class PDF(FPDF):
    """
    Шаблон создания PDF списка покупок

    >>> pdf = PDF()
    >>> pdf.get_pdf(html_text=None)
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
        self.set_font('Montserrat', 'B', size=22)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(127, 84, 178)
        self.rect(0, 0, 500, 25, style='F')
        self.cell(0, 7, 'Список покупок', align='C')
        self.image(LOGO, 10, 7, 33)
        self.ln(20)

    def footer(self) -> None:
        link = os.getenv('FOODGRAM_LINK')
        if link is None:
            return

        self.set_y(-15)
        self.set_text_color(128)
        text_link = link.split('://', 1)[-1]
        self.cell(0, 10, text_link, align='R', link=link)

    def get_pdf(self, html_text=None):
        if self.page == 0:
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
    pdf.set_font('Montserrat', 'I', size=14)
    pdf.set_text_color(0, 0, 0)
    for recipe in recipes:
        pdf.cell(
            0, 6, recipe, align='L', border='B', new_x='LEFT', new_y='NEXT'
        )
    pdf.ln(6)
    pdf.set_font('Montserrat', '', size=12)
    pdf_file = pdf.get_pdf(html)
    return pdf_file
