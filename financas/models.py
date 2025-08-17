from django.db import models
from django.contrib.auth.models import User

class Transacao(models.Model):
    # A "etiqueta" que diz a qual usuário esta transação pertence.
    # on_delete=models.CASCADE significa: se o usuário for deletado, apague as transações dele também.
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    data = models.DateField()
    
    # Um campo de texto com escolhas pré-definidas para evitar erros de digitação.
    TIPO_CHOICES = [
        ("RECEITA", "Receita"),
        ("DESPESA", "Despesa"),
    ]
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    
    descricao = models.CharField(max_length=200)
    
    # O tipo de campo correto para dinheiro. Evita problemas de arredondamento.
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    
    categoria = models.CharField(max_length=50)

    # Isso ajuda a exibir as transações de forma legível no painel de administração.
    def __str__(self):
        return f"[{self.data}] {self.descricao} - R$ {self.valor}"