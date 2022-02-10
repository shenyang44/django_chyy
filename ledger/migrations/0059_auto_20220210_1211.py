# Generated by Django 3.1.6 on 2022-02-10 04:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0058_transaction_off_vouch_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='off_vouch_no',
            field=models.IntegerField(null=True, unique=True, validators=[django.core.validators.MinValueValidator(21001)]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='receipt_no',
            field=models.IntegerField(null=True, unique=True, validators=[django.core.validators.MinValueValidator(30501)]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='vouch_no',
            field=models.IntegerField(null=True, unique=True, validators=[django.core.validators.MinValueValidator(43001)]),
        ),
    ]
