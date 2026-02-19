from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Transacao, CartaoCredito
from .forms import TransacaoForm, CartaoCreditoForm


@login_required
def dashboard(request):
    """Exibe o painel principal com o resumo financeiro."""
    transacoes = Transacao.objects.filter(usuario=request.user)
    
    # Cálculos totais
    total_receitas = transacoes.filter(tipo="RECEITA").aggregate(Sum("valor"))["valor__sum"] or 0
    total_despesas = transacoes.filter(tipo="DESPESA").aggregate(Sum("valor"))["valor__sum"] or 0
    
    # Cálculos do mês atual
    agora = datetime.now()
    transacoes_mes = transacoes.filter(data__year=agora.year, data__month=agora.month)
    receitas_mes = transacoes_mes.filter(tipo="RECEITA").aggregate(Sum("valor"))["valor__sum"] or 0
    despesas_mes = transacoes_mes.filter(tipo="DESPESA").aggregate(Sum("valor"))["valor__sum"] or 0
    
    contexto = {
        "saldo_total": total_receitas - total_despesas,
        "receitas_mes": receitas_mes,
        "despesas_mes": despesas_mes,
        "ultimos_lancamentos": transacoes.order_by("-data")[:5],
    }
    return render(request, "financas/dashboard.html", contexto)


@login_required
def lista_transacoes(request):
    """Lista as transações com paginação."""
    transacoes_list = Transacao.objects.filter(usuario=request.user)
    paginator = Paginator(transacoes_list, 10)
    transacoes = paginator.get_page(request.GET.get('page'))
    
    return render(request, "financas/lista_transacoes.html", {"transacoes": transacoes})


@login_required
def adicionar_transacao(request):
    """Adiciona uma nova transação."""
    form = TransacaoForm(request.POST or None, user=request.user)
    
    if request.method == "POST" and form.is_valid():
        transacao = form.save(commit=False)
        transacao.usuario = request.user
        transacao.save()
        return redirect("lista_transacoes")

    return render(request, "financas/adicionar_transacao.html", {"form": form})


@login_required
def remover_transacao(request, pk):
    """Remove uma transação com confirmação."""
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)
    
    if request.method == "POST":
        transacao.delete()
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


class CartaoCreditoCreateView(BaseCartaoCreditoView, CreateView):
    form_class = CartaoCreditoForm
    template_name = "financas/cartao_credito_form.html"

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class CartaoCreditoUpdateView(BaseCartaoCreditoView, UpdateView):
    form_class = CartaoCreditoForm
    template_name = "financas/cartao_credito_form.html"


class CartaoCreditoDeleteView(BaseCartaoCreditoView, DeleteView):
    template_name = "financas/confirm_delete.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'cartão de crédito'
        return context
