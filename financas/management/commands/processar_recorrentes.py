from django.core.management.base import BaseCommand
from django.utils import timezone

from financas.models import TransacaoRecorrente, Transacao


class Command(BaseCommand):
    help = 'Cria transações a partir dos templates recorrentes com próxima ocorrência vencida.'

    def handle(self, *args, **kwargs):
        hoje = timezone.localdate()
        pendentes = TransacaoRecorrente.objects.filter(
            ativa=True,
            proxima_ocorrencia__lte=hoje,
        ).select_related('usuario', 'categoria', 'cartao_credito')

        criadas = 0
        for rec in pendentes:
            Transacao.objects.create(
                usuario=rec.usuario,
                tipo=rec.tipo,
                descricao=rec.descricao,
                valor=rec.valor,
                categoria=rec.categoria,
                cartao_credito=rec.cartao_credito,
                data=rec.proxima_ocorrencia,
            )
            rec.avancar_proxima_ocorrencia()
            criadas += 1

        self.stdout.write(self.style.SUCCESS(f'{criadas} transacoes criadas com sucesso.'))
