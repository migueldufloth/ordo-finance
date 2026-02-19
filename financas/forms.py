from django import forms
from .models import Transacao, Categoria, CartaoCredito

TAILWIND_INPUT_STYLE = 'w-full px-3 py-2 border border-gray-300 rounded-lg'

class TransacaoForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.none(),
        required=True,
        empty_label="-- Selecione uma Categoria --", 
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_STYLE})
    )
    cartao_credito = forms.ModelChoiceField(
        queryset=CartaoCredito.objects.none(),
        required=False,
        empty_label="-- Nenhum --",
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_STYLE})
    )

    class Meta:
        model = Transacao
        fields = ['data', 'tipo', 'descricao', 'valor', 'categoria', 'cartao_credito']
        widgets = {
            'tipo': forms.Select(attrs={'class': TAILWIND_INPUT_STYLE}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_STYLE}),
            'descricao': forms.TextInput(attrs={'class': TAILWIND_INPUT_STYLE, 'placeholder': 'Ex: Salário, Aluguel'}),
            'valor': forms.NumberInput(attrs={'class': TAILWIND_INPUT_STYLE, 'step': '0.01'}),
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