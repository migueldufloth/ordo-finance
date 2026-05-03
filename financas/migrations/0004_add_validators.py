import decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financas', '0003_alter_cartaocredito_cor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartaocredito',
            name='dia_fechamento',
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(31),
                ],
                verbose_name='Dia do Fechamento',
            ),
        ),
        migrations.AlterField(
            model_name='cartaocredito',
            name='dia_vencimento',
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(31),
                ],
                verbose_name='Dia do Vencimento',
            ),
        ),
        migrations.AlterField(
            model_name='cartaocredito',
            name='limite',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(decimal.Decimal('0.01'))],
            ),
        ),
        migrations.AlterField(
            model_name='transacao',
            name='valor',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(decimal.Decimal('0.01'))],
            ),
        ),
    ]
