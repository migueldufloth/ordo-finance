from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)

    class Meta:
        unique_together = ('usuario', 'nome')
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome

class CartaoCredito(models.Model):
    class Cor(models.TextChoices):
        AZUL = "BLUE", "Azul"
        VERDE = "GREEN", "Verde"
        VERMELHO = "RED", "Vermelho"
        ROXO = "PURPLE", "Roxo"
        PRETO = "BLACK", "Preto"
        LARANJA = "ORANGE", "Laranja"
        CINZA = "GRAY", "Cinza"

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, verbose_name="Nome do Cartão")
    limite = models.DecimalField(max_digits=10, decimal_places=2)
    dia_fechamento = models.IntegerField(verbose_name="Dia do Fechamento")
    dia_vencimento = models.IntegerField(verbose_name="Dia do Vencimento")
    cor = models.CharField(
        max_length=6, 
        choices=Cor.choices, 
        default=Cor.CINZA, 
        verbose_name="Cor do Cartão"
    )

    class Meta:
        verbose_name = "Cartão de Crédito"
        verbose_name_plural = "Cartões de Crédito"

    def __str__(self):
        return self.nome

class Transacao(models.Model):
    class Tipo(models.TextChoices):
        RECEITA = "RECEITA", "Receita"
        DESPESA = "DESPESA", "Despesa"

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    data = models.DateField()
    tipo = models.CharField(max_length=7, choices=Tipo.choices)
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    cartao_credito = models.ForeignKey(
        CartaoCredito, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name="Cartão de Crédito"
    )
    fatura_paga = models.BooleanField(default=False, verbose_name="Fatura Paga")

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ['-data']

    def __str__(self):
        return f"[{self.data}] {self.descricao} - R$ {self.valor}"












    