# Generated by Django 3.1.6 on 2022-02-11 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0060_auto_20220210_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='receipt_ref',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='voucher_ref',
            field=models.TextField(null=True),
        ),
    ]
