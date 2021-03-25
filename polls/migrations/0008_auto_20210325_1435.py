# Generated by Django 3.1.6 on 2021-03-25 06:35

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_auto_20210325_0122'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='total',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 25, 6, 35, 19, 786383, tzinfo=utc)),
        ),
    ]
