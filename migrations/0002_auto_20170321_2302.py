# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-03-21 22:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('alertas', '0001_squashed_0020_auto_20170305_2320'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertaHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('con', 'Concursos de acreedores'), ('liq', 'Liquidación de empresas'), ('new', 'Empresas de nueva creación'), ('company', 'Empresa'), ('person', 'Persona')], max_length=10)),
                ('date', models.DateField()),
                ('provincia', models.CharField(blank=True, max_length=3, null=True)),
                ('entidad', models.CharField(blank=True, max_length=260, null=True)),
                ('periodicidad', models.CharField(blank=True, choices=[('weekly', 'Semanal'), ('monthly', 'Mensual'), ('daily', 'Diario')], max_length=10, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='lbinvoice',
            name='nif',
            field=models.CharField(max_length=20),
        ),
    ]
