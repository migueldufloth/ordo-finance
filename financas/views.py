import csv
import decimal

import requests as http_requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Transacao, CartaoCredito, Categoria, Orcamento, FaturaCartao, TransacaoRecorrente
from .forms import TransacaoForm, CartaoCreditoForm, CategoriaForm, OrcamentoForm, TransacaoRecorrenteForm

MESES = [
    (1,'Janeiro'),(2,'Fevereiro'),(3,'Março'),(4,'Abril'),
    (5,'Maio'),(6,'Junho'),(7,'Julho'),(8,'Agosto'),
    (9,'Setembro'),(10,'Outubro'),(11,'Novembro'),(12,'Dezembro'),
]


@login_required
def dashboard(request):
    """Exibe o painel principal com resumo financeiro, gráficos e orçamentos."""
    import json
    from dateutil.relativedelta import relativedelta
    from django.db.models.functions import TruncMonth

    usuario = request.user
    hoje = timezone.localdate()

    try:
        ano = int(request.GET.get('ano', hoje.year))
        mes = int(request.GET.get('mes', hoje.month))
        if not (1 <= mes <= 12):
            mes = hoje.month
    except (ValueError, TypeError):
        ano, mes = hoje.year, hoje.month

    transacoes = Transacao.objects.filter(usuario=usuario)
    transacoes_mes = transacoes.filter(data__year=ano, data__month=mes)

    receitas_mes = transacoes_mes.filter(tipo='RECEITA').aggregate(Sum('valor'))['valor__sum'] or 0
    despesas_mes = transacoes_mes.filter(tipo='DESPESA').aggregate(Sum('valor'))['valor__sum'] or 0
    total_receitas = transacoes.filter(tipo='RECEITA').aggregate(Sum('valor'))['valor__sum'] or 0
    total_despesas = transacoes.filter(tipo='DESPESA').aggregate(Sum('valor'))['valor__sum'] or 0

    # Gráfico 1: Gastos por categoria no mês (donut)
    gastos_cat = list(
        transacoes_mes.filter(tipo='DESPESA')
        .values('categoria__nome')
        .annotate(total=Sum('valor'))
        .order_by('-total')
    )
    chart_categorias = json.dumps({
        'labels': [g['categoria__nome'] for g in gastos_cat],
        'data': [float(g['total']) for g in gastos_cat],
    })

    # Gráfico 2: Receita vs Despesa — últimos 6 meses (bar)
    inicio_6m = (hoje.replace(day=1) - relativedelta(months=5))
    evolucao = list(
        transacoes.filter(data__gte=inicio_6m)
        .annotate(mes_trunc=TruncMonth('data'))
        .values('mes_trunc', 'tipo')
        .annotate(total=Sum('valor'))
        .order_by('mes_trunc')
    )
    MESES_PT = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    labels_6m, receitas_bar, despesas_bar = [], [], []
    cursor = inicio_6m
    for _ in range(6):
        labels_6m.append(f"{MESES_PT[cursor.month - 1]}/{str(cursor.year)[-2:]}")
        rec = next((float(e['total']) for e in evolucao
                    if e['mes_trunc'].year == cursor.year and e['mes_trunc'].month == cursor.month
                    and e['tipo'] == 'RECEITA'), 0)
        desp = next((float(e['total']) for e in evolucao
                     if e['mes_trunc'].year == cursor.year and e['mes_trunc'].month == cursor.month
                     and e['tipo'] == 'DESPESA'), 0)
        receitas_bar.append(rec)
        despesas_bar.append(desp)
        cursor = cursor + relativedelta(months=1)
    chart_evolucao = json.dumps({'labels': labels_6m, 'receitas': receitas_bar, 'despesas': despesas_bar})

    # Gráfico 3: Saldo acumulado — últimos 6 meses (line)
    saldo_base = float(
        transacoes.filter(data__lt=inicio_6m, tipo='RECEITA').aggregate(Sum('valor'))['valor__sum'] or 0
    ) - float(
        transacoes.filter(data__lt=inicio_6m, tipo='DESPESA').aggregate(Sum('valor'))['valor__sum'] or 0
    )
    saldo_acumulado = []
    saldo_cursor = saldo_base
    cursor = inicio_6m
    for i in range(6):
        saldo_cursor += receitas_bar[i] - despesas_bar[i]
        saldo_acumulado.append(round(saldo_cursor, 2))
        cursor = cursor + relativedelta(months=1)
    chart_saldo = json.dumps({'labels': labels_6m, 'saldo': saldo_acumulado})

    # Orçamentos com gasto do mês selecionado — mais críticos primeiro
    orcamentos = list(Orcamento.objects.filter(usuario=usuario).select_related('categoria'))
    for o in orcamentos:
        o.gasto_mes = transacoes_mes.filter(
            tipo='DESPESA', categoria=o.categoria).aggregate(Sum('valor'))['valor__sum'] or decimal.Decimal('0')
        o.disponivel = max(o.valor_mensal - o.gasto_mes, decimal.Decimal('0'))
        o.percentual = min(int(o.gasto_mes / o.valor_mensal * 100), 100) if o.valor_mensal else 0
    orcamentos.sort(key=lambda o: o.percentual, reverse=True)

    # Cartões com uso do limite no mês selecionado
    cartoes = list(CartaoCredito.objects.filter(usuario=usuario))
    for c in cartoes:
        c.gasto_mes = transacoes_mes.filter(
            tipo='DESPESA', cartao_credito=c).aggregate(Sum('valor'))['valor__sum'] or decimal.Decimal('0')
        c.percentual_limite = min(int(c.gasto_mes / c.limite * 100), 100) if c.limite else 0

    anos_lista = list(range(2023, hoje.year + 1))

    return render(request, 'financas/dashboard.html', {
        'saldo_total': total_receitas - total_despesas,
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'ultimos_lancamentos': transacoes.order_by('-data')[:5],
        'ano': ano,
        'mes': mes,
        'meses_lista': MESES,
        'anos_lista': anos_lista,
        'chart_categorias': chart_categorias,
        'chart_evolucao': chart_evolucao,
        'chart_saldo': chart_saldo,
        'orcamentos': orcamentos,
        'cartoes': cartoes,
    })


def _filtrar_transacoes(request):
    """Retorna queryset de transações do usuário aplicando os filtros da query string."""
    qs = Transacao.objects.filter(usuario=request.user).select_related('categoria', 'cartao_credito')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(descricao__icontains=q)
    tipo = request.GET.get('tipo')
    if tipo in ('RECEITA', 'DESPESA'):
        qs = qs.filter(tipo=tipo)
    mes = request.GET.get('mes', '').strip()
    ano = request.GET.get('ano', '').strip()
    if mes and ano:
        try:
            qs = qs.filter(data__month=int(mes), data__year=int(ano))
        except ValueError:
            pass
    categoria_pk = request.GET.get('categoria', '').strip()
    if categoria_pk:
        try:
            qs = qs.filter(categoria__pk=int(categoria_pk))
        except ValueError:
            pass
    cartao_pk = request.GET.get('cartao', '').strip()
    if cartao_pk:
        try:
            qs = qs.filter(cartao_credito__pk=int(cartao_pk))
        except ValueError:
            pass
    return qs


@login_required
def lista_transacoes(request):
    """Lista as transações com filtros e paginação server-side."""
    qs = _filtrar_transacoes(request)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    categorias = Categoria.objects.filter(usuario=request.user)
    cartoes = CartaoCredito.objects.filter(usuario=request.user)
    hoje = timezone.localdate()
    anos = list(range(2023, hoje.year + 1))

    return render(request, "financas/lista_transacoes.html", {
        'page_obj': page_obj,
        'categorias': categorias,
        'cartoes': cartoes,
        'anos': anos,
        'meses': MESES,
        'filtros': request.GET,
    })


@login_required
def exportar_csv(request):
    """Exporta as transações filtradas como CSV compatível com Excel."""
    qs = _filtrar_transacoes(request)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="transacoes-ordo.csv"'
    response.write('﻿')  # BOM UTF-8 para Excel
    writer = csv.writer(response)
    writer.writerow(['Data', 'Descrição', 'Tipo', 'Valor', 'Categoria', 'Cartão'])
    for t in qs:
        writer.writerow([
            t.data.strftime('%d/%m/%Y'),
            t.descricao,
            t.get_tipo_display(),
            f'{t.valor:.2f}'.replace('.', ','),
            t.categoria.nome if t.categoria else '',
            t.cartao_credito.nome if t.cartao_credito else '',
        ])
    return response


@login_required
def adicionar_transacao(request):
    """Adiciona uma nova transação."""
    form = TransacaoForm(request.POST or None, user=request.user)
    
    if request.method == "POST" and form.is_valid():
        transacao = form.save(commit=False)
        transacao.usuario = request.user
        transacao.save()
        messages.success(request, "Lançamento adicionado com sucesso.")
        return redirect("lista_transacoes")

    return render(request, "financas/adicionar_transacao.html", {"form": form})


@login_required
def editar_transacao(request, pk):
    """Edita uma transação existente."""
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)
    form = TransacaoForm(request.POST or None, instance=transacao, user=request.user)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Lançamento atualizado com sucesso.")
        return redirect("lista_transacoes")

    return render(request, "financas/adicionar_transacao.html", {"form": form, "editando": True, "transacao": transacao})


@login_required
def remover_transacao(request, pk):
    """Remove uma transação com confirmação."""
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)
    
    if request.method == "POST":
        transacao.delete()
        messages.success(request, "Lançamento removido.")
        return redirect("lista_transacoes")
        
    return render(request, "financas/confirm_delete.html", {"object": transacao, "type": "transação"})


# Mixin e Base View para Cartões de Crédito para DRY
class BaseCartaoCreditoView(LoginRequiredMixin):
    model = CartaoCredito
    success_url = reverse_lazy("cartao_credito_list")

    def get_queryset(self):
        return CartaoCredito.objects.filter(usuario=self.request.user)


class CartaoCreditoListView(BaseCartaoCreditoView, ListView):
    template_name = "financas/cartao_credito_list.html"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        transacoes_mes = Transacao.objects.filter(
            usuario=self.request.user,
            tipo='DESPESA',
            data__year=hoje.year,
            data__month=hoje.month,
        )
        for cartao in context['object_list']:
            cartao.gasto_mes = transacoes_mes.filter(
                cartao_credito=cartao).aggregate(Sum('valor'))['valor__sum'] or decimal.Decimal('0')
            cartao.percentual_limite = min(
                int(cartao.gasto_mes / cartao.limite * 100), 100) if cartao.limite else 0
        return context


class CartaoCreditoCreateView(BaseCartaoCreditoView, CreateView):
    form_class = CartaoCreditoForm
    template_name = "financas/cartao_credito_form.html"

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Cartão criado com sucesso.")
        return super().form_valid(form)


class CartaoCreditoUpdateView(BaseCartaoCreditoView, UpdateView):
    form_class = CartaoCreditoForm
    template_name = "financas/cartao_credito_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Cartão atualizado com sucesso.")
        return super().form_valid(form)


class CartaoCreditoDeleteView(BaseCartaoCreditoView, DeleteView):
    template_name = "financas/confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Cartão removido.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'cartão de crédito'
        return context

# Mixin e Base View para Categorias
class BaseCategoriaView(LoginRequiredMixin):
    model = Categoria
    success_url = reverse_lazy("categoria_list")

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)

class CategoriaListView(BaseCategoriaView, ListView):
    template_name = "financas/categoria_list.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            super().get_queryset()
            .annotate(total_transacoes=Count('transacao'))
            .order_by('nome')
        )

class CategoriaCreateView(BaseCategoriaView, CreateView):
    form_class = CategoriaForm
    template_name = "financas/categoria_form.html"

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Categoria criada com sucesso.")
        return super().form_valid(form)

class CategoriaUpdateView(BaseCategoriaView, UpdateView):
    form_class = CategoriaForm
    template_name = "financas/categoria_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Categoria atualizada com sucesso.")
        return super().form_valid(form)

class CategoriaDeleteView(BaseCategoriaView, DeleteView):
    template_name = "financas/confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Categoria removida.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'categoria'
        return context


@login_required
def gerar_relatorio(request):
    _MESES = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    qs = _filtrar_transacoes(request)

    mes = request.GET.get('mes', '').strip()
    ano = request.GET.get('ano', '').strip()
    try:
        periodo = f'{_MESES[int(mes)]}/{ano}' if mes and ano else 'Todos os lançamentos'
    except (ValueError, IndexError):
        periodo = 'Todos os lançamentos'

    payload = {
        'usuario': request.user.username,
        'periodo': periodo,
        'transacoes': [
            {
                'descricao': t.descricao,
                'valor': float(t.valor),
                'tipo': t.tipo,
                'data': t.data.isoformat(),
                'categoria': t.categoria.nome if t.categoria else '',
            }
            for t in qs
        ],
    }

    try:
        resp = http_requests.post(
            settings.REPORTS_API_URL + '/relatorio/pdf',
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
    except Exception:
        messages.error(request, 'Não foi possível gerar o relatório. Tente novamente.')
        return redirect('lista_transacoes')

    response = HttpResponse(resp.content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio-ordo.pdf"'
    return response


# ─── Orçamento ────────────────────────────────────────────────────────────────

class BaseOrcamentoView(LoginRequiredMixin):
    model = Orcamento
    success_url = reverse_lazy('orcamento_list')

    def get_queryset(self):
        return Orcamento.objects.filter(usuario=self.request.user).select_related('categoria')


class OrcamentoListView(BaseOrcamentoView, ListView):
    template_name = 'financas/orcamento_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        try:
            ano = int(self.request.GET.get('ano', hoje.year))
            mes = int(self.request.GET.get('mes', hoje.month))
            if not (1 <= mes <= 12):
                mes = hoje.month
        except (ValueError, TypeError):
            ano, mes = hoje.year, hoje.month

        transacoes_mes = Transacao.objects.filter(
            usuario=self.request.user,
            tipo='DESPESA',
            data__year=ano,
            data__month=mes,
        )
        for o in context['object_list']:
            o.gasto_mes = transacoes_mes.filter(categoria=o.categoria).aggregate(
                Sum('valor'))['valor__sum'] or decimal.Decimal('0')
            o.disponivel = max(o.valor_mensal - o.gasto_mes, decimal.Decimal('0'))
            o.percentual = min(int(o.gasto_mes / o.valor_mensal * 100), 100) if o.valor_mensal else 0

        context['mes'] = mes
        context['ano'] = ano
        context['meses_lista'] = MESES
        context['anos_lista'] = list(range(2023, hoje.year + 1))
        return context


class OrcamentoCreateView(BaseOrcamentoView, CreateView):
    form_class = OrcamentoForm
    template_name = 'financas/orcamento_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Orçamento criado com sucesso.')
        return super().form_valid(form)


class OrcamentoUpdateView(BaseOrcamentoView, UpdateView):
    form_class = OrcamentoForm
    template_name = 'financas/orcamento_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Orçamento atualizado com sucesso.')
        return super().form_valid(form)


class OrcamentoDeleteView(BaseOrcamentoView, DeleteView):
    template_name = 'financas/confirm_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'Orçamento removido.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'orçamento'
        return context


# ─── Fatura do Cartão ──────────────────────────────────────────────────────────

@login_required
def fatura_cartao(request, pk):
    """Exibe as transações de um cartão num período e o status da fatura."""
    from datetime import date as date_type
    cartao = get_object_or_404(CartaoCredito, pk=pk, usuario=request.user)
    mes_ref_str = request.GET.get('mes')
    if mes_ref_str:
        try:
            mes_ref = date_type.fromisoformat(mes_ref_str + '-01')
        except ValueError:
            mes_ref = timezone.localdate().replace(day=1)
    else:
        mes_ref = timezone.localdate().replace(day=1)

    fatura, _ = FaturaCartao.objects.get_or_create(
        cartao_credito=cartao,
        mes_referencia=mes_ref,
        defaults={'usuario': request.user},
    )
    transacoes = Transacao.objects.filter(
        usuario=request.user,
        cartao_credito=cartao,
        data__year=mes_ref.year,
        data__month=mes_ref.month,
    ).select_related('categoria')
    total = transacoes.aggregate(Sum('valor'))['valor__sum'] or decimal.Decimal('0')
    percentual_limite = min(int(total / cartao.limite * 100), 100) if cartao.limite else 0

    from dateutil.relativedelta import relativedelta
    mes_anterior = (mes_ref - relativedelta(months=1)).strftime('%Y-%m')
    mes_proximo = (mes_ref + relativedelta(months=1)).strftime('%Y-%m')

    return render(request, 'financas/fatura_cartao.html', {
        'cartao': cartao,
        'fatura': fatura,
        'transacoes': transacoes,
        'total': total,
        'mes_ref': mes_ref,
        'percentual_limite': percentual_limite,
        'mes_anterior': mes_anterior,
        'mes_proximo': mes_proximo,
    })


@login_required
def marcar_fatura_paga(request, pk):
    """Alterna o status de pagamento de uma fatura."""
    fatura = get_object_or_404(FaturaCartao, pk=pk, usuario=request.user)
    if request.method == 'POST':
        fatura.paga = not fatura.paga
        fatura.data_pagamento = timezone.localdate() if fatura.paga else None
        fatura.save()
        messages.success(request, 'Fatura marcada como paga.' if fatura.paga else 'Fatura desmarcada.')
    return redirect(f"{reverse_lazy('fatura_cartao', kwargs={'pk': fatura.cartao_credito.pk})}?mes={fatura.mes_referencia.strftime('%Y-%m')}")


# ─── Transações Recorrentes ───────────────────────────────────────────────────

class BaseTransacaoRecorrenteView(LoginRequiredMixin):
    model = TransacaoRecorrente
    success_url = reverse_lazy('transacao_recorrente_list')

    def get_queryset(self):
        return TransacaoRecorrente.objects.filter(usuario=self.request.user).select_related('categoria', 'cartao_credito')


class TransacaoRecorrenteListView(BaseTransacaoRecorrenteView, ListView):
    template_name = 'financas/transacao_recorrente_list.html'


class TransacaoRecorrenteCreateView(BaseTransacaoRecorrenteView, CreateView):
    form_class = TransacaoRecorrenteForm
    template_name = 'financas/transacao_recorrente_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Transação recorrente criada com sucesso.')
        return super().form_valid(form)


class TransacaoRecorrenteUpdateView(BaseTransacaoRecorrenteView, UpdateView):
    form_class = TransacaoRecorrenteForm
    template_name = 'financas/transacao_recorrente_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Transação recorrente atualizada.')
        return super().form_valid(form)


class TransacaoRecorrenteDeleteView(BaseTransacaoRecorrenteView, DeleteView):
    template_name = 'financas/confirm_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'Transação recorrente removida.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'transação recorrente'
        return context
