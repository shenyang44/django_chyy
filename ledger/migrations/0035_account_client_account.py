# Generated by Django 3.1.6 on 2021-04-27 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0034_remove_account_client_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='client_account',
            field=models.BooleanField(default=False),
        ),
    ]
