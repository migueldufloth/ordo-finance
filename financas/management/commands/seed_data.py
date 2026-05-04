import random
from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from financas.models import CartaoCredito, Categoria, Transacao


class Command(BaseCommand):
    help = "Popula o banco com dados fictícios simulando uso real (6 meses)"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, help="Username do usuário alvo")
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Remove transações, cartões e categorias do usuário antes de inserir",
        )

    def handle(self, *args, **options):
        usuario = self._get_usuario(options.get("username"))
        if not usuario:
            return

        if options["limpar"]:
            Transacao.objects.filter(usuario=usuario).delete()
            CartaoCredito.objects.filter(usuario=usuario).delete()
            Categoria.objects.filter(usuario=usuario).delete()
            self.stdout.write(self.style.WARNING(f'Dados de "{usuario.username}" removidos.'))

        self.stdout.write(f"Populando dados para: {self.style.SUCCESS(usuario.username)}\n")

        cats = self._criar_categorias(usuario)
        cartoes = self._criar_cartoes(usuario)
        total = self._criar_transacoes(usuario, cats, cartoes)

        self.stdout.write(self.style.SUCCESS(f"\nOK — {total} transacoes inseridas."))

    # ------------------------------------------------------------------ helpers

    def _get_usuario(self, username):
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Usuário "{username}" não encontrado.'))
                return None

        usuario = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not usuario:
            self.stdout.write(self.style.ERROR("Nenhum usuário encontrado. Crie um antes."))
            return None
        return usuario

    def _criar_categorias(self, usuario):
        nomes = [
            "Salário", "Freelance", "Investimentos",
            "Moradia", "Alimentação", "Restaurantes", "Transporte",
            "Saúde", "Farmácia", "Educação", "Lazer",
            "Vestuário", "Serviços Digitais", "Pets", "Outros",
        ]
        cats = {}
        for nome in nomes:
            obj, _ = Categoria.objects.get_or_create(usuario=usuario, nome=nome)
            cats[nome] = obj
        self.stdout.write(f"  {len(cats)} categorias criadas")
        return cats

    def _criar_cartoes(self, usuario):
        dados = [
            {"nome": "Nubank",  "cor": "PURPLE", "limite": Decimal("5000.00"), "dia_fechamento": 1,  "dia_vencimento": 8},
            {"nome": "Inter",   "cor": "ORANGE", "limite": Decimal("3000.00"), "dia_fechamento": 10, "dia_vencimento": 17},
            {"nome": "C6 Bank", "cor": "BLACK",  "limite": Decimal("8000.00"), "dia_fechamento": 5,  "dia_vencimento": 12},
        ]
        cartoes = {}
        for d in dados:
            obj, _ = CartaoCredito.objects.get_or_create(
                usuario=usuario, nome=d["nome"], defaults=d
            )
            cartoes[d["nome"]] = obj
        self.stdout.write(f"  {len(cartoes)} cartões criados")
        return cartoes

    def _criar_transacoes(self, usuario, cats, cartoes):
        today = date.today()
        nubank, inter, c6 = cartoes["Nubank"], cartoes["Inter"], cartoes["C6 Bank"]
        total = 0

        for offset in range(5, -1, -1):
            ano = today.year
            mes = today.month - offset
            while mes <= 0:
                mes += 12
                ano -= 1

            ultimo_dia = monthrange(ano, mes)[1]
            is_mes_atual = (ano == today.year and mes == today.month)

            def d(dia):
                dia = min(dia, ultimo_dia)
                dt = date(ano, mes, dia)
                return dt if dt <= today else None

            def pago(mes_offset):
                return mes_offset > 0

            # ── RECEITAS ──────────────────────────────────────────────────────

            dt = d(5)
            if dt:
                self._t(usuario, dt, "RECEITA", "Salário", "6800.00", cats["Salário"])
                total += 1

            if random.random() < 0.55:
                dt = d(random.randint(8, 25))
                if dt:
                    val = random.choice(["900.00", "1200.00", "1500.00", "2000.00", "2500.00"])
                    desc = random.choice(["Projeto freelance", "Consultoria", "Design UI/UX", "Dev web", "Revisão de sistema"])
                    self._t(usuario, dt, "RECEITA", desc, val, cats["Freelance"])
                    total += 1

            if random.random() < 0.3:
                dt = d(random.randint(15, 28))
                if dt:
                    val = f"{random.randint(80, 350)}.00"
                    self._t(usuario, dt, "RECEITA", "Dividendos / rendimentos", val, cats["Investimentos"])
                    total += 1

            # ── DESPESAS FIXAS ────────────────────────────────────────────────

            dt = d(1)
            if dt:
                self._t(usuario, dt, "DESPESA", "Aluguel", "1400.00", cats["Moradia"])
                total += 1

            dt = d(2)
            if dt:
                self._t(usuario, dt, "DESPESA", "Condomínio", "350.00", cats["Moradia"])
                total += 1

            dt = d(10)
            if dt:
                self._t(usuario, dt, "DESPESA", "Plano de saúde", "289.00", cats["Saúde"])
                total += 1

            dt = d(5)
            if dt:
                self._t(usuario, dt, "DESPESA", "Academia SmartFit", "109.90", cats["Saúde"], inter, pago(offset))
                total += 1

            dt = d(12)
            if dt:
                self._t(usuario, dt, "DESPESA", "Netflix", "45.90", cats["Serviços Digitais"], nubank, pago(offset))
                total += 1

            dt = d(8)
            if dt:
                self._t(usuario, dt, "DESPESA", "Spotify", "21.90", cats["Serviços Digitais"], nubank, pago(offset))
                total += 1

            dt = d(15)
            if dt:
                self._t(usuario, dt, "DESPESA", "Internet fibra", "120.00", cats["Serviços Digitais"])
                total += 1

            # ── DESPESAS VARIÁVEIS ────────────────────────────────────────────

            # Conta de luz
            dt = d(random.randint(10, 20))
            if dt:
                val = f"{random.randint(95, 210)}.{random.choice(['00', '43', '78'])}"
                self._t(usuario, dt, "DESPESA", "Conta de luz", val, cats["Moradia"])
                total += 1

            # Água
            dt = d(random.randint(5, 15))
            if dt:
                val = f"{random.randint(55, 95)}.{random.choice(['00', '20', '60'])}"
                self._t(usuario, dt, "DESPESA", "Conta de água", val, cats["Moradia"])
                total += 1

            # Combustível (2-3x)
            postos = ["Posto Shell", "Posto Petrobras", "Posto Ipiranga", "Auto Posto Central"]
            for _ in range(random.randint(2, 3)):
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = f"{random.randint(130, 230)}.{random.choice(['00', '50', '90'])}"
                    self._t(usuario, dt, "DESPESA", random.choice(postos), val, cats["Transporte"])
                    total += 1

            # Supermercado (2-3x)
            mercados = ["Carrefour", "Pão de Açúcar", "Extra", "Mercadinho do bairro", "Atacadão"]
            for _ in range(random.randint(2, 3)):
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = f"{random.randint(140, 420)}.{random.choice(['00', '30', '75'])}"
                    cartao = random.choice([None, None, c6])
                    self._t(usuario, dt, "DESPESA", random.choice(mercados), val, cats["Alimentação"], cartao, pago(offset))
                    total += 1

            # Restaurantes / delivery (4-7x)
            restaurantes = [
                "iFood — Burger King", "Sushi Hana", "Restaurante Família", "McDonald's",
                "Pizza Hut", "Outback Steakhouse", "iFood — Pizza", "Padaria & Café",
                "Lanchonete Central", "Temakeria do Parque",
            ]
            for _ in range(random.randint(4, 7)):
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = f"{random.randint(28, 135)}.{random.choice(['00', '90', '50'])}"
                    cartao = random.choice([None, None, nubank, c6])
                    self._t(usuario, dt, "DESPESA", random.choice(restaurantes), val, cats["Restaurantes"], cartao, pago(offset))
                    total += 1

            # Transporte urbano (2-5x)
            for _ in range(random.randint(2, 5)):
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = f"{random.randint(12, 58)}.{random.choice(['00', '90'])}"
                    self._t(usuario, dt, "DESPESA", random.choice(["Uber", "99 Táxi", "Metrô", "Ônibus"]), val, cats["Transporte"])
                    total += 1

            # Farmácia (0-2x)
            for _ in range(random.randint(0, 2)):
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = f"{random.randint(22, 195)}.{random.choice(['00', '90', '50'])}"
                    self._t(usuario, dt, "DESPESA", random.choice(["Drogasil", "Droga Raia", "Ultrafarma", "Farmácia Popular"]), val, cats["Farmácia"])
                    total += 1

            # Vestuário (40% chance)
            if random.random() < 0.4:
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = f"{random.randint(79, 480)}.{random.choice(['00', '90'])}"
                    cartao = random.choice([nubank, c6])
                    self._t(usuario, dt, "DESPESA", random.choice(["Renner", "Zara", "C&A", "H&M", "Hering", "Adidas Store"]), val, cats["Vestuário"], cartao, pago(offset))
                    total += 1

            # Lazer (0-2x)
            for _ in range(random.randint(0, 2)):
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = f"{random.randint(28, 95)}.{random.choice(['00', '50'])}"
                    cartao = random.choice([None, nubank])
                    self._t(usuario, dt, "DESPESA", random.choice(["Cinema", "Show", "Parque", "Boliche", "Escape Room", "Balada"]), val, cats["Lazer"], cartao, pago(offset))
                    total += 1

            # Pets (35% chance)
            if random.random() < 0.35:
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = f"{random.randint(45, 310)}.{random.choice(['00', '90'])}"
                    self._t(usuario, dt, "DESPESA", random.choice(["Ração Royal Canin", "Petshop — banho", "Vet Clínica", "Petlove"]), val, cats["Pets"])
                    total += 1

            # Saúde pontual (30% chance)
            if random.random() < 0.3:
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = random.choice(["200.00", "250.00", "300.00", "350.00"])
                    self._t(usuario, dt, "DESPESA", random.choice(["Consulta médica", "Dentista", "Psicólogo", "Oftalmologista"]), val, cats["Saúde"])
                    total += 1

            # Educação (25% chance)
            if random.random() < 0.25:
                dt = d(random.randint(1, ultimo_dia))
                if dt:
                    val = random.choice(["29.90", "39.90", "49.90", "99.90", "197.00"])
                    self._t(usuario, dt, "DESPESA", random.choice(["Udemy", "Alura", "Coursera", "Livro técnico"]), val, cats["Educação"], nubank, pago(offset))
                    total += 1

        return total

    def _t(self, usuario, data, tipo, descricao, valor, categoria, cartao=None, fatura_paga=False):
        Transacao.objects.create(
            usuario=usuario,
            data=data,
            tipo=tipo,
            descricao=descricao,
            valor=Decimal(valor),
            categoria=categoria,
            cartao_credito=cartao,
            fatura_paga=fatura_paga,
        )
