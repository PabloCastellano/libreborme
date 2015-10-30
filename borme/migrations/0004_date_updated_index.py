# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borme', '0003_auto_20151029_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='date_updated',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='date_updated',
            field=models.DateField(db_index=True),
        ),
    ]
