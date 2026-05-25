from django.urls import path
from .views import (
    lista_transacoes,
    adicionar_transacao,
    editar_transacao,
    remover_transacao,
    gerar_relatorio,
    exportar_csv,
    CartaoCreditoListView,
    CartaoCreditoCreateView,
    CartaoCreditoUpdateView,
    CartaoCreditoDeleteView,
    CategoriaListView,
    CategoriaCreateView,
    CategoriaUpdateView,
    CategoriaDeleteView,
    OrcamentoListView,
    OrcamentoCreateView,
    OrcamentoUpdateView,
    OrcamentoDeleteView,
    fatura_cartao,
    marcar_fatura_paga,
    TransacaoRecorrenteListView,
    TransacaoRecorrenteCreateView,
    TransacaoRecorrenteUpdateView,
    TransacaoRecorrenteDeleteView,
)

urlpatterns = [
    # Transações
    path('', lista_transacoes, name='lista_transacoes'),
    path('adicionar/', adicionar_transacao, name='adicionar_transacao'),
    path('<int:pk>/editar/', editar_transacao, name='editar_transacao'),
    path('<int:pk>/remover/', remover_transacao, name='remover_transacao'),
    path('relatorio/', gerar_relatorio, name='gerar_relatorio'),
    path('exportar-csv/', exportar_csv, name='exportar_csv'),

    # Cartões de crédito
    path('cartoes/', CartaoCreditoListView.as_view(), name='cartao_credito_list'),
    path('cartoes/adicionar/', CartaoCreditoCreateView.as_view(), name='cartao_credito_create'),
    path('cartoes/<int:pk>/editar/', CartaoCreditoUpdateView.as_view(), name='cartao_credito_update'),
    path('cartoes/<int:pk>/remover/', CartaoCreditoDeleteView.as_view(), name='cartao_credito_delete'),
    path('cartoes/<int:pk>/fatura/', fatura_cartao, name='fatura_cartao'),
    path('faturas/<int:pk>/pagar/', marcar_fatura_paga, name='marcar_fatura_paga'),

    # Categorias
    path('categorias/', CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/adicionar/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/remover/', CategoriaDeleteView.as_view(), name='categoria_delete'),

    # Orçamentos
    path('orcamentos/', OrcamentoListView.as_view(), name='orcamento_list'),
    path('orcamentos/adicionar/', OrcamentoCreateView.as_view(), name='orcamento_create'),
    path('orcamentos/<int:pk>/editar/', OrcamentoUpdateView.as_view(), name='orcamento_update'),
    path('orcamentos/<int:pk>/remover/', OrcamentoDeleteView.as_view(), name='orcamento_delete'),

    # Transações recorrentes
    path('recorrentes/', TransacaoRecorrenteListView.as_view(), name='transacao_recorrente_list'),
    path('recorrentes/adicionar/', TransacaoRecorrenteCreateView.as_view(), name='transacao_recorrente_create'),
    path('recorrentes/<int:pk>/editar/', TransacaoRecorrenteUpdateView.as_view(), name='transacao_recorrente_update'),
    path('recorrentes/<int:pk>/remover/', TransacaoRecorrenteDeleteView.as_view(), name='transacao_recorrente_delete'),
]