# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-26 15:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alertas', '0004_auto_20170225_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertaacto',
            name='notification',
            field=models.CharField(choices=[('U', 'URL'), ('E', 'E-mail')], default='E', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='alertaacto',
            name='evento',
            field=models.CharField(choices=[('CON', 'Concursos de acreedores'), ('LIQ', 'Liquidación de empresas')], max_length=3),
        ),
        migrations.AlterField(
            model_name='alertaacto',
            name='periodicidad',
            field=models.CharField(choices=[('W', 'Semanal'), ('M', 'Mensual'), ('D', 'Diario')], max_length=1),
        ),
        migrations.AlterField(
            model_name='lbinvoice',
            name='payment_type',
            field=models.CharField(choices=[('Paypal', 'Paypal'), ('Bank', 'Bank transfer'), ('Bitcoin', 'Bitcoin')], max_length=10),
        ),
    ]
