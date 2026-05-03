from datetime import date
from typing import List

from fastapi import FastAPI
from fastapi.responses import Response
from fpdf import FPDF
from pydantic import BaseModel

app = FastAPI(title="Ordo Finance API", description="Microserviço de relatórios")


class TransacaoItem(BaseModel):
    data: str
    descricao: str
    tipo: str
    valor: str
    categoria: str = ""


class RelatorioRequest(BaseModel):
    usuario: str
    transacoes: List[TransacaoItem]


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "reports-api"}


@app.get("/")
def root():
    return {"message": "Microserviço de relatórios (FastAPI) em operação"}


@app.post("/relatorio/pdf")
def gerar_pdf(dados: RelatorioRequest):
    pdf = FPDF()
    pdf.add_page()

    # Cabeçalho
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Ordo Finance - Relatório de Transações", ln=True, align="C")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, f"Usuário: {dados.usuario}", ln=True)
    pdf.cell(0, 8, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(4)

    # Cabeçalho da tabela
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(28, 8, "Data", border=1, fill=True)
    pdf.cell(72, 8, "Descrição", border=1, fill=True)
    pdf.cell(38, 8, "Categoria", border=1, fill=True)
    pdf.cell(26, 8, "Tipo", border=1, fill=True)
    pdf.cell(26, 8, "Valor (R$)", border=1, fill=True, ln=True)

    # Linhas
    pdf.set_font("Helvetica", size=9)
    total_receitas = 0.0
    total_despesas = 0.0

    for t in dados.transacoes:
        valor = float(t.valor)
        if t.tipo == "RECEITA":
            total_receitas += valor
        else:
            total_despesas += valor

        pdf.cell(28, 7, t.data, border=1)
        pdf.cell(72, 7, t.descricao[:45], border=1)
        pdf.cell(38, 7, t.categoria[:22], border=1)
        pdf.cell(26, 7, t.tipo, border=1)
        pdf.cell(26, 7, f"{valor:.2f}", border=1, ln=True, align="R")

    # Totais
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, f"Total Receitas:  R$ {total_receitas:.2f}", ln=True)
    pdf.cell(0, 8, f"Total Despesas:  R$ {total_despesas:.2f}", ln=True)
    pdf.cell(0, 8, f"Saldo:           R$ {(total_receitas - total_despesas):.2f}", ln=True)

    return Response(content=bytes(pdf.output()), media_type="application/pdf")
