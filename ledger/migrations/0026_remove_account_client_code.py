# Generated by Django 3.1.6 on 2021-04-14 03:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0025_auto_20210414_1105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='client_code',
        ),
    ]