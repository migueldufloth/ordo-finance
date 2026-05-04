import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse

from .models import Categoria, CartaoCredito, Transacao


def criar_usuario(username='usuario', password='senha123'):
    return User.objects.create_user(username=username, password=password)


def criar_categoria(usuario, nome='Alimentação'):
    return Categoria.objects.create(usuario=usuario, nome=nome)


def criar_transacao(usuario, categoria, descricao='Salário', valor='1000.00', tipo='RECEITA'):
    return Transacao.objects.create(
        usuario=usuario,
        data=datetime.date.today(),
        tipo=tipo,
        descricao=descricao,
        valor=valor,
        categoria=categoria,
    )


class TransacaoValidatorTest(TestCase):
    """Validators do model Transacao."""

    def setUp(self):
        self.usuario = criar_usuario()
        self.categoria = criar_categoria(self.usuario)

    def test_valor_negativo_e_rejeitado(self):
        transacao = Transacao(
            usuario=self.usuario,
            data=datetime.date.today(),
            tipo='RECEITA',
            descricao='Teste',
            valor='-50.00',
            categoria=self.categoria,
        )
        with self.assertRaises(ValidationError):
            transacao.full_clean()

    def test_valor_zero_e_rejeitado(self):
        transacao = Transacao(
            usuario=self.usuario,
            data=datetime.date.today(),
            tipo='DESPESA',
            descricao='Teste',
            valor='0.00',
            categoria=self.categoria,
        )
        with self.assertRaises(ValidationError):
            transacao.full_clean()


class CartaoCreditoValidatorTest(TestCase):
    """Validators do model CartaoCredito."""

    def setUp(self):
        self.usuario = criar_usuario()

    def test_dia_fechamento_zero_e_rejeitado(self):
        cartao = CartaoCredito(
            usuario=self.usuario,
            nome='Nubank',
            limite='1000.00',
            dia_fechamento=0,
            dia_vencimento=10,
            cor='BLUE',
        )
        with self.assertRaises(ValidationError):
            cartao.full_clean()

    def test_dia_vencimento_acima_de_31_e_rejeitado(self):
        cartao = CartaoCredito(
            usuario=self.usuario,
            nome='Nubank',
            limite='1000.00',
            dia_fechamento=10,
            dia_vencimento=32,
            cor='BLUE',
        )
        with self.assertRaises(ValidationError):
            cartao.full_clean()


class CategoriaIntegridadeTest(TestCase):
    """Regras de integridade do model Categoria."""

    def setUp(self):
        self.usuario = criar_usuario()

    def test_categoria_duplicada_mesmo_usuario_e_bloqueada(self):
        criar_categoria(self.usuario, nome='Transporte')
        with self.assertRaises(IntegrityError):
            criar_categoria(self.usuario, nome='Transporte')

    def test_categoria_mesmo_nome_usuarios_diferentes_e_permitida(self):
        outro_usuario = criar_usuario(username='outro')
        criar_categoria(self.usuario, nome='Transporte')
        categoria2 = criar_categoria(outro_usuario, nome='Transporte')
        self.assertEqual(categoria2.nome, 'Transporte')


class AutenticacaoTest(TestCase):
    """Proteção de rotas por autenticação."""

    def test_dashboard_sem_login_redireciona_para_login(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_lista_transacoes_sem_login_redireciona_para_login(self):
        response = self.client.get(reverse('lista_transacoes'))
        self.assertRedirects(response, '/accounts/login/?next=/transacoes/')


class IsolamentoDadosTest(TestCase):
    """Garantia de que cada usuário só enxerga seus próprios dados."""

    def setUp(self):
        self.user1 = criar_usuario(username='user1')
        self.user2 = criar_usuario(username='user2')
        categoria = criar_categoria(self.user1)
        criar_transacao(self.user1, categoria, descricao='Receita do user1')

    def test_usuario_nao_ve_transacoes_de_outro(self):
        self.client.login(username='user2', password='senha123')
        response = self.client.get(reverse('lista_transacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['transacoes']), 0)

    def test_criar_transacao_associa_ao_usuario_logado(self):
        categoria = criar_categoria(self.user2, nome='Salário')
        self.client.login(username='user2', password='senha123')
        self.client.post(reverse('adicionar_transacao'), {
            'data': datetime.date.today(),
            'tipo': 'RECEITA',
            'descricao': 'Freelance',
            'valor': '500.00',
            'categoria': categoria.pk,
        })
        transacao = Transacao.objects.get(descricao='Freelance')
        self.assertEqual(transacao.usuario, self.user2)
