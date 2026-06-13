import io
from collections import defaultdict
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from fpdf import FPDF
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

MESES_PT = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

CORES = ['#4f46e5', '#22c55e', '#f59e0b', '#ef4444',
         '#14b8a6', '#a855f7', '#f97316', '#94a3b8']

app = FastAPI(title='Ordo Finance — Relatórios')


class TransacaoItem(BaseModel):
    descricao: str
    valor: float
    tipo: str
    data: str
    categoria: str


class RelatorioRequest(BaseModel):
    usuario: str
    periodo: str
    transacoes: list[TransacaoItem]


def _fmt_num(valor: float) -> str:
    return f'{abs(valor):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def _brl(valor: float) -> str:
    s = _fmt_num(valor)
    return f'-R$ {s}' if valor < 0 else f'R$ {s}'


def _fig_to_buf(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=140, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


def _pizza_categorias(transacoes: list[TransacaoItem]) -> io.BytesIO | None:
    gastos: dict[str, float] = defaultdict(float)
    for t in transacoes:
        if t.tipo == 'DESPESA':
            gastos[t.categoria or 'Sem categoria'] += t.valor
    if not gastos:
        return None

    itens = sorted(gastos.items(), key=lambda x: x[1], reverse=True)
    if len(itens) > 7:
        top = itens[:7]
        outros = sum(v for _, v in itens[7:])
        top.append(('Outros', outros))
    else:
        top = itens

    labels = [k for k, _ in top]
    values = [v for _, v in top]

    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    wedges, _, autotexts = ax.pie(
        values,
        labels=None,
        autopct='%1.1f%%',
        colors=CORES[:len(values)],
        startangle=90,
        pctdistance=0.72,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white', 'width': 0.62},
    )
    for at in autotexts:
        at.set_fontsize(7.5)
    ax.legend(
        wedges, labels,
        loc='lower center', bbox_to_anchor=(0.5, -0.22),
        ncol=3, fontsize=7, frameon=False,
    )
    ax.set_title('Despesas por Categoria', fontsize=10, fontweight='bold', pad=10)
    fig.subplots_adjust(bottom=0.22)

    return _fig_to_buf(fig)


def _barras_mensal(transacoes: list[TransacaoItem]) -> io.BytesIO | None:
    meses: dict[str, dict[str, float]] = defaultdict(lambda: {'r': 0.0, 'd': 0.0})
    for t in transacoes:
        m = t.data[:7]
        if t.tipo == 'RECEITA':
            meses[m]['r'] += t.valor
        else:
            meses[m]['d'] += t.valor
    if not meses:
        return None

    sorted_m = sorted(meses.keys())
    labels = [f"{MESES_PT[int(m[5:7]) - 1]}/{m[2:4]}" for m in sorted_m]
    receitas = [meses[m]['r'] for m in sorted_m]
    despesas = [meses[m]['d'] for m in sorted_m]

    x = list(range(len(labels)))
    bar_w = 0.38

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.bar([i - bar_w / 2 for i in x], receitas, bar_w,
           label='Receitas', color='#22c55e', alpha=0.88)
    ax.bar([i + bar_w / 2 for i in x], despesas, bar_w,
           label='Despesas', color='#ef4444', alpha=0.88)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f'R${v / 1000:.0f}k' if v >= 1000 else f'R${v:.0f}')
    )
    ax.tick_params(axis='y', labelsize=7.5)
    ax.legend(fontsize=8.5, frameon=False)
    ax.set_title('Receitas vs Despesas por Mês', fontsize=10, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle='--', alpha=0.35)
    plt.tight_layout()

    return _fig_to_buf(fig)


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'reports'}


@app.post('/relatorio/pdf')
def relatorio_pdf(req: RelatorioRequest):
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pw = pdf.w - 30  # largura útil

    # ── Página 1: cabeçalho + resumo + gráficos ──────────────────────────────
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 11, 'Ordo Finance', ln=True, align='C')

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'Relatório de Transações', ln=True, align='C')

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(0, 5, f'Usuário: {req.usuario}   |   Período: {req.periodo}', ln=True, align='C')
    pdf.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}', ln=True, align='C')
    pdf.ln(6)

    # Cards de resumo
    total_r = sum(t.valor for t in req.transacoes if t.tipo == 'RECEITA')
    total_d = sum(t.valor for t in req.transacoes if t.tipo == 'DESPESA')
    saldo = total_r - total_d
    w_card = pw / 3
    y_card = pdf.get_y()

    for i, (label, valor, cor) in enumerate([
        ('RECEITAS', total_r, (34, 197, 94)),
        ('DESPESAS', total_d, (239, 68, 68)),
        ('SALDO', saldo, (79, 70, 229) if saldo >= 0 else (239, 68, 68)),
    ]):
        x = 15 + i * w_card
        pdf.set_fill_color(246, 246, 252)
        pdf.rect(x, y_card, w_card - 2, 19, style='F')
        pdf.set_xy(x + 3, y_card + 3)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(w_card - 6, 4, label, ln=True)
        pdf.set_xy(x + 3, y_card + 8)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*cor)
        pdf.cell(w_card - 6, 8, _brl(valor))

    pdf.set_xy(15, y_card + 24)
    pdf.set_text_color(30, 30, 30)

    # Gráficos
    pizza = _pizza_categorias(req.transacoes)
    barras = _barras_mensal(req.transacoes)
    y_charts = pdf.get_y()

    if pizza and barras:
        pdf.image(pizza, x=15, y=y_charts, w=pw * 0.46)
        pdf.image(barras, x=15 + pw * 0.48, y=y_charts, w=pw * 0.52)
        pdf.set_y(y_charts + 74)
    elif pizza:
        pdf.image(pizza, x=15 + pw * 0.2, y=y_charts, w=pw * 0.6)
        pdf.set_y(y_charts + 74)
    elif barras:
        pdf.image(barras, x=15, y=y_charts, w=pw)
        pdf.set_y(y_charts + 60)

    # ── Página 2: tabela de lançamentos ──────────────────────────────────────
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, f'Lançamentos ({len(req.transacoes)})', ln=True)
    pdf.ln(1)

    cw = [22, 68, 30, 22, 23]
    cabecalhos = ['Data', 'Descrição', 'Categoria', 'Tipo', 'Valor (R$)']

    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_fill_color(79, 70, 229)
    pdf.set_text_color(255, 255, 255)
    aligns = ['C', 'L', 'L', 'C', 'C']
    for w, h, a in zip(cw, cabecalhos, aligns):
        pdf.cell(w, 7, h, fill=True, align=a)
    pdf.ln()

    pdf.set_font('Helvetica', '', 8)
    for idx, t in enumerate(req.transacoes):
        zebra = idx % 2 == 1
        pdf.set_fill_color(245, 245, 252) if zebra else pdf.set_fill_color(255, 255, 255)

        data = t.data[8:10] + '/' + t.data[5:7] + '/' + t.data[:4]
        cor_tipo = (22, 163, 74) if t.tipo == 'RECEITA' else (220, 38, 38)
        label_tipo = 'Receita' if t.tipo == 'RECEITA' else 'Despesa'

        pdf.set_text_color(60, 60, 60)
        pdf.cell(cw[0], 6, data, fill=zebra, align='C')
        pdf.cell(cw[1], 6, t.descricao[:42], fill=zebra)
        pdf.cell(cw[2], 6, (t.categoria or '')[:20], fill=zebra)
        pdf.set_text_color(*cor_tipo)
        pdf.cell(cw[3], 6, label_tipo, fill=zebra, align='C')
        pdf.set_text_color(60, 60, 60)
        pdf.cell(cw[4], 6, _fmt_num(t.valor), fill=zebra, align='R')
        pdf.ln()

        if pdf.get_y() > pdf.h - 25:
            pdf.add_page()

    return Response(content=bytes(pdf.output()), media_type='application/pdf')
