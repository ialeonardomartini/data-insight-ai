import re
import io
import pandas as pd
import plotly.io as pio
from fpdf import FPDF


def remover_emojis(texto: str) -> str:
    return re.sub(r'[^\x00-\x7F]+', '', texto)


class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Arial", size=12)

    def add_paragraph(self, text: str):
        text = remover_emojis(text)
        for line in text.strip().split("\n"):
            self.multi_cell(0, 10, line.strip())
            self.ln(0.5)

    def add_plotly_figure(self, fig, title: str = ""):
        if title:
            self.set_font("Arial", 'B', 14)
            self.multi_cell(0, 10, remover_emojis(title))
            self.ln()

        # Exporta a figura como PNG em memória
        img_bytes = io.BytesIO()
        pio.write_image(fig, img_bytes, format='png', width=700, height=400, scale=2)
        img_bytes.seek(0)

        self.image(img_bytes, w=180, type="PNG")
        self.ln()

    def add_table(self, dataframe: pd.DataFrame, title: str = ""):
        if title:
            self.add_paragraph(f"\n{title}")

        # Cálculo da largura efetiva da página
        col_width = (self.w - 2 * self.l_margin) / len(dataframe.columns)

        self.set_font("Arial", size=10)
        for col in dataframe.columns:
            self.cell(col_width, 10, str(col), border=1)
        self.ln()

        for _, row in dataframe.iterrows():
            for item in row:
                self.cell(col_width, 10, str(item), border=1)
            self.ln()


def gerar_relatorio_completo(
    df: pd.DataFrame,
    qualidade: str,
    insights: str,
    graficos: list,
    perguntas_respostas: str,
    kpis: dict
) -> bytes:
    pdf = PDFReport()

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Relatório de Análise - E-commerce", ln=True, align='C')
    pdf.ln(10)

    # Qualidade dos Dados
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Qualidade dos Dados", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.add_paragraph(qualidade)

    # Insights
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Insights de Negócio", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.add_paragraph(insights)

    # KPIs Estratégicos
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. KPIs Estratégicos", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.add_paragraph(
        f"🎯 Ticket Médio por Pedido: R$ {kpis['ticket_medio_pedido']}\n"
        f"🛍️ Ticket Médio por Cliente: R$ {kpis['ticket_medio_cliente']}\n"
        f"🔁 Média de Pedidos por Cliente: {kpis['media_pedidos_por_cliente']}"
    )

    # Faturamento por Categoria (tabela)
    faturamento = pd.Series(kpis["faturamento_categoria"]).reset_index()
    faturamento.columns = ["Categoria", "Faturamento"]
    pdf.add_table(faturamento, title="💰 Faturamento por Categoria")

    # Top 5 Clientes
    top = pd.Series(kpis["top_clientes"]).reset_index()
    top.columns = ["Cliente", "Valor Total"]
    pdf.add_table(top, title="🥇 Top 5 Clientes")

    # Gráficos com descrição
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "4. Gráficos Gerados", ln=True)
    pdf.ln(5)

    for grafico in graficos:
        pdf.add_plotly_figure(grafico["fig"], title=grafico["descricao"])

    # Perguntas e Respostas
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "5. Perguntas Respondidas", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.add_paragraph(perguntas_respostas)

    # Exporta como bytes
    return pdf.output(dest="S").encode("latin1")
