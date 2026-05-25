from django import forms
from .models import Transacao, Categoria, CartaoCredito, Orcamento, TransacaoRecorrente

TAILWIND_INPUT_STYLE = 'w-full px-3 py-2 border border-gray-300 rounded-lg'

class TransacaoForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.none(),
        required=True,
        empty_label="",
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_STYLE})
    )
    cartao_credito = forms.ModelChoiceField(
        queryset=CartaoCredito.objects.none(),
        required=False,
        empty_label="",
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_STYLE})
    )

    class Meta:
        model = Transacao
        fields = ['data', 'tipo', 'descricao', 'valor', 'categoria', 'cartao_credito', 'fatura_paga']
        widgets = {
            'tipo': forms.Select(attrs={'class': TAILWIND_INPUT_STYLE}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_STYLE}),
            'descricao': forms.TextInput(attrs={'class': TAILWIND_INPUT_STYLE, 'placeholder': 'Ex: Salário, Aluguel'}),
            'valor': forms.NumberInput(attrs={'class': TAILWIND_INPUT_STYLE, 'step': '0.01'}),
            'fatura_paga': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user)
            self.fields['cartao_credito'].queryset = CartaoCredito.objects.filter(usuario=user)
            
class CartaoCreditoForm(forms.ModelForm):
    class Meta:
        model = CartaoCredito
        fields = ['nome', 'cor', 'limite', 'dia_fechamento', 'dia_vencimento']
        widgets = {
            'nome': forms.TextInput(attrs={'class': TAILWIND_INPUT_STYLE, 'placeholder': 'Ex: Nubank Platinum'}),
            'cor': forms.Select(attrs={'class': TAILWIND_INPUT_STYLE}),
            'limite': forms.NumberInput(attrs={'class': TAILWIND_INPUT_STYLE, 'step': '0.01'}),
            'dia_fechamento': forms.NumberInput(attrs={'class': TAILWIND_INPUT_STYLE, 'min': '1', 'max': '31'}),
            'dia_vencimento': forms.NumberInput(attrs={'class': TAILWIND_INPUT_STYLE, 'min': '1', 'max': '31'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': TAILWIND_INPUT_STYLE, 'placeholder': 'Ex: Alimentação, Transporte'}),
        }


class OrcamentoForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.none(),
        required=True,
        empty_label='Selecione uma categoria',
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_STYLE}),
    )

    class Meta:
        model = Orcamento
        fields = ['categoria', 'valor_mensal']
        widgets = {
            'valor_mensal': forms.NumberInput(attrs={'class': TAILWIND_INPUT_STYLE, 'step': '0.01', 'placeholder': '0,00'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            used_ids = Orcamento.objects.filter(usuario=user).values_list('categoria_id', flat=True)
            qs = Categoria.objects.filter(usuario=user)
            if self.instance.pk:
                qs = qs.exclude(pk__in=used_ids) | qs.filter(pk=self.instance.categoria_id)
            else:
                qs = qs.exclude(pk__in=used_ids)
            self.fields['categoria'].queryset = qs


class TransacaoRecorrenteForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.none(),
        required=True,
        empty_label='Selecione uma categoria',
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_STYLE}),
    )
    cartao_credito = forms.ModelChoiceField(
        queryset=CartaoCredito.objects.none(),
        required=False,
        empty_label='Nenhum',
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_STYLE}),
    )

    class Meta:
        model = TransacaoRecorrente
        fields = ['tipo', 'descricao', 'valor', 'categoria', 'cartao_credito', 'frequencia', 'proxima_ocorrencia', 'ativa']
        widgets = {
            'tipo': forms.Select(attrs={'class': TAILWIND_INPUT_STYLE}),
            'descricao': forms.TextInput(attrs={'class': TAILWIND_INPUT_STYLE, 'placeholder': 'Ex: Salário, Aluguel'}),
            'valor': forms.NumberInput(attrs={'class': TAILWIND_INPUT_STYLE, 'step': '0.01'}),
            'frequencia': forms.Select(attrs={'class': TAILWIND_INPUT_STYLE}),
            'proxima_ocorrencia': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_STYLE}),
            'ativa': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-primary-600 rounded border-gray-300'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user)
            self.fields['cartao_credito'].queryset = CartaoCredito.objects.filter(usuario=user)