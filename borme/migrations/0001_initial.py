# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anuncio',
            fields=[
                ('id_anuncio', models.IntegerField(serialize=False, primary_key=True)),
                ('year', models.IntegerField()),
                ('datos_registrales', models.CharField(max_length=70)),
                ('actos', django_hstore.fields.SerializedDictionaryField()),
            ],
        ),
        migrations.CreateModel(
            name='Borme',
            fields=[
                ('cve', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('date', models.DateField()),
                ('url', models.URLField()),
                ('from_reg', models.IntegerField()),
                ('until_reg', models.IntegerField()),
                ('province', models.CharField(max_length=100)),
                ('section', models.CharField(max_length=20)),
                ('anuncios', django.contrib.postgres.fields.ArrayField(size=None, base_field=models.IntegerField(), default=list)),
            ],
        ),
        migrations.CreateModel(
            name='BormeLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_parsed', models.DateTimeField(null=True, blank=True)),
                ('parsed', models.BooleanField(default=False)),
                ('errors', models.IntegerField(default=0)),
                ('path', models.CharField(max_length=200)),
                ('borme', models.ForeignKey(to='borme.Borme')),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(db_index=True, max_length=250)),
                ('nif', models.CharField(max_length=10)),
                ('slug', models.CharField(unique=True, max_length=250)),
                ('date_creation', models.DateField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=False)),
                ('type', models.CharField(max_length=50, choices=[('SAL', 'Sociedad Anónima Laboral'), ('SRLP', 'Sociedad de Responsabilidad Limitada Profesional'), ('SCP', 'Sociedad Civil Profesional'), ('SRL', 'Sociedad de Responsabilidad Limitada'), ('SLNE', 'Sociedad Limitada Nueva Empresa'), ('SAU', 'Sociedad Anónima Unipersonal'), ('SRLL', 'Sociedad de Responsabilidad Limitada Laboral'), ('AIE', 'Agrupación de Interés Económico'), ('SLP', 'Sociedad Limitada Profesional'), ('SLU', 'Sociedad Limitada Unipersonal'), ('COOP', 'Cooperativa'), ('SAP', 'Sociedad Anónima P?'), ('SLL', 'Sociedad Limitada Laboral'), ('SA', 'Sociedad Anónima'), ('SL', 'Sociedad Limitada')])),
                ('in_bormes', django.contrib.postgres.fields.ArrayField(size=None, base_field=django_hstore.fields.DictionaryField(), default=list)),
                ('anuncios', django.contrib.postgres.fields.ArrayField(size=None, base_field=models.IntegerField(), default=list)),
                ('cargos_actuales_p', django.contrib.postgres.fields.ArrayField(size=None, base_field=django_hstore.fields.DictionaryField(), default=list)),
                ('cargos_actuales_c', django.contrib.postgres.fields.ArrayField(size=None, base_field=django_hstore.fields.DictionaryField(), default=list)),
                ('cargos_historial_p', django.contrib.postgres.fields.ArrayField(size=None, base_field=django_hstore.fields.DictionaryField(), default=list)),
                ('cargos_historial_c', django.contrib.postgres.fields.ArrayField(size=None, base_field=django_hstore.fields.DictionaryField(), default=list)),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('last_modified', models.DateTimeField()),
                ('version', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('slug', models.CharField(unique=True, max_length=200)),
                ('in_companies', django.contrib.postgres.fields.ArrayField(size=None, base_field=models.CharField(max_length=250), default=list)),
                ('in_bormes', django.contrib.postgres.fields.ArrayField(size=None, base_field=django_hstore.fields.DictionaryField(), default=list)),
                ('cargos_actuales', django.contrib.postgres.fields.ArrayField(size=None, base_field=django_hstore.fields.DictionaryField(), default=list)),
                ('cargos_historial', django.contrib.postgres.fields.ArrayField(size=None, base_field=django_hstore.fields.DictionaryField(), default=list)),
            ],
        ),
        migrations.AddField(
            model_name='anuncio',
            name='borme',
            field=models.ForeignKey(to='borme.Borme'),
        ),
        migrations.AddField(
            model_name='anuncio',
            name='company',
            field=models.ForeignKey(to='borme.Company'),
        ),
        migrations.AlterIndexTogether(
            name='anuncio',
            index_together=set([('id_anuncio', 'year')]),
        ),
    ]
