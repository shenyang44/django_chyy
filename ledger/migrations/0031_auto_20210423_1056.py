# Generated by Django 3.1.6 on 2021-04-23 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0030_running_balance_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='type_code',
        ),
        migrations.AddField(
            model_name='transaction',
            name='type_codes',
            field=models.TextField(default='[ex]'),
            preserve_default=False,
        ),
    ]
