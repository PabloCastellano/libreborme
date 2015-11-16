# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borme', '0004_date_updated_index'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bormelog',
            name='id',
        ),
        migrations.AlterField(
            model_name='bormelog',
            name='borme',
            field=models.OneToOneField(to='borme.Borme', serialize=False, primary_key=True),
        ),
    ]
