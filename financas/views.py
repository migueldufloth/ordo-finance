from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
import requests

from .models import Transacao, CartaoCredito, Categoria
from .forms import TransacaoForm, CartaoCreditoForm, CategoriaForm


@login_required
def dashboard(request):
    """Exibe o painel principal com o resumo financeiro."""
    transacoes = Transacao.objects.filter(usuario=request.user)
    
    # Cálculos totais
    total_receitas = transacoes.filter(tipo="RECEITA").aggregate(Sum("valor"))["valor__sum"] or 0
    total_despesas = transacoes.filter(tipo="DESPESA").aggregate(Sum("valor"))["valor__sum"] or 0
    
    # Cálculos do mês atual (timezone-aware para America/Sao_Paulo)
    hoje = timezone.localdate()
    transacoes_mes = transacoes.filter(data__year=hoje.year, data__month=hoje.month)
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
    """Delega a geração do PDF ao microserviço FastAPI e retorna o arquivo."""
    transacoes = Transacao.objects.filter(usuario=request.user).select_related('categoria')
    dados = {
        "usuario": request.user.username,
        "transacoes": [
            {
                "data": str(t.data),
                "descricao": t.descricao,
                "tipo": t.tipo,
                "valor": str(t.valor),
                "categoria": t.categoria.nome if t.categoria else "",
            }
            for t in transacoes
        ],
    }
    try:
        resposta = requests.post(
            f"{settings.REPORTS_API_URL}/relatorio/pdf",
            json=dados,
            timeout=30,
        )
        resposta.raise_for_status()
    except requests.exceptions.RequestException:
        messages.error(request, "Não foi possível gerar o relatório. Verifique se o serviço está disponível.")
        return redirect("lista_transacoes")

    response = HttpResponse(resposta.content, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="relatorio-ordo.pdf"'
    return response
