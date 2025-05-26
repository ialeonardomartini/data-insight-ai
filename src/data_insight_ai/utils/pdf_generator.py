from fpdf import FPDF
from io import BytesIO
from typing import List
import plotly.graph_objects as go
import pandas as pd
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
        self.cell(0, 10, limpar_texto_para_pdf(str(text)), ln=True, align='C')
        self.ln(10)
        self.set_font("Arial", size=12)

    def add_paragraph(self, text):
        if not isinstance(text, str):
            text = str(text)  # ✅ Converte CrewOutput, Pydantic, etc

        for line in text.strip().split("\n"):
            clean_line = limpar_texto_para_pdf(line)
            self.multi_cell(0, 10, clean_line)
        self.ln()

    def add_image(self, path, title=None):
        if title:
            self.set_font("Arial", 'B', 12)
            clean_title = limpar_texto_para_pdf(str(title))
            self.multi_cell(0, 10, clean_title)
            self.ln(1)
        self.image(path, w=180)
        self.ln(5)


def gerar_relatorio_completo(df, qualidade, insights, graficos, perguntas_respostas) -> BytesIO:
    pdf = PDF()
    pdf.add_title("Relatório Completo de Análise de Dados - DataInsightAI")

    # 1. Tabela
    pdf.add_title("📄 Amostra da Tabela de Dados")
    pdf.add_paragraph(df.head(10).to_csv(index=False))

    # 2. Qualidade
    pdf.add_title("🧪 Avaliação da Qualidade dos Dados")
    pdf.add_paragraph(qualidade)

    # 3. Insights
    pdf.add_title("🧠 Insights Gerados")
    pdf.add_paragraph(insights)

    # 4. Gráficos
    pdf.add_title("📊 Visualizações com Análise")
    for grafico in graficos:
        fig: go.Figure = grafico.get("fig")
        titulo: str = grafico.get("descricao", "Gráfico")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.write_image(tmpfile.name, format="png")
            pdf.add_image(tmpfile.name, title=titulo)
    
    # 5. Q&A com IA
    if perguntas_respostas:
        pdf.add_title("💬 Perguntas e Respostas sobre os Dados")
        for pergunta, resposta in perguntas_respostas:
            pdf.add_paragraph(f"👤 Pergunta: {pergunta}")
            pdf.add_paragraph(f"🤖 Resposta: {resposta}")

    # Finaliza
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return buffer
