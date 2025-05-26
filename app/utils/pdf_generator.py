from fpdf import FPDF
from io import BytesIO
from typing import List
import plotly.graph_objects as go
import tempfile


def limpar_texto_para_pdf(texto: str) -> str:
    return texto.encode("latin-1", "ignore").decode("latin-1")


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Arial", size=12)

    def add_title(self, text):
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, limpar_texto_para_pdf(text), ln=True, align='C')
        self.ln(10)
        self.set_font("Arial", size=12)

    def add_paragraph(self, text):
        for line in text.strip().split("\n"):
            clean_line = limpar_texto_para_pdf(line)
            self.multi_cell(0, 10, clean_line)
        self.ln()

    def add_image(self, path, title=None):
        if title:
            self.set_font("Arial", 'B', 12)
            clean_title = limpar_texto_para_pdf(title)
            self.multi_cell(0, 10, clean_title)
            self.ln(1)
        self.image(path, w=180)
        self.ln(5)


def gerar_relatorio_com_graficos(texto: str, graficos: List[dict]) -> BytesIO:
    pdf = PDF()
    pdf.add_title("Relatorio de Analise de Dados - DataInsightAI")
    pdf.add_paragraph(texto)

    for grafico in graficos:
        fig: go.Figure = grafico["fig"]
        titulo: str = grafico["titulo"]

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.write_image(tmpfile.name, format="png")
            pdf.add_image(tmpfile.name, title=titulo)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return buffer