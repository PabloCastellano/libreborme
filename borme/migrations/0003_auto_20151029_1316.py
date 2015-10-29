# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borme', '0002_auto_20151027_0226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='id',
        ),
        migrations.RemoveField(
            model_name='person',
            name='id',
        ),
        migrations.AlterField(
            model_name='company',
            name='slug',
            field=models.CharField(primary_key=True, max_length=250, serialize=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='type',
            field=models.CharField(max_length=50, choices=[('AIE', 'Agrupación de Interés Económico'), ('COOP', 'Cooperativa'), ('SA', 'Sociedad Anónima'), ('SAL', 'Sociedad Anónima Laboral'), ('SAP', 'Sociedad Anónima P?'), ('SAU', 'Sociedad Anónima Unipersonal'), ('SCP', 'Sociedad Civil Profesional'), ('SL', 'Sociedad Limitada'), ('SLL', 'Sociedad Limitada Laboral'), ('SLNE', 'Sociedad Limitada Nueva Empresa'), ('SLP', 'Sociedad Limitada Profesional'), ('SLU', 'Sociedad Limitada Unipersonal'), ('SRL', 'Sociedad de Responsabilidad Limitada'), ('SRLL', 'Sociedad de Responsabilidad Limitada Laboral'), ('SRLP', 'Sociedad de Responsabilidad Limitada Profesional')]),
        ),
        migrations.AlterField(
            model_name='person',
            name='slug',
            field=models.CharField(primary_key=True, max_length=200, serialize=False),
        ),
    ]
