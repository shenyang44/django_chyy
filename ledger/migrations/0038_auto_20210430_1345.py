# Generated by Django 3.1.6 on 2021-04-30 05:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0037_transaction_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='settled',
            new_name='resolved',
        ),
    ]