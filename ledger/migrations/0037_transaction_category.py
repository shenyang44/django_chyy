# Generated by Django 3.1.6 on 2021-04-28 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0036_auto_20210427_2030'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='category',
            field=models.CharField(default='ad', max_length=2),
            preserve_default=False,
        ),
    ]
