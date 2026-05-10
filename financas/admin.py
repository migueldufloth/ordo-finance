from django.contrib import admin
from .models import Transacao, CartaoCredito, Categoria 

admin.site.register(Transacao)
admin.site.register(CartaoCredito)
admin.site.register(Categoria)