# Generated by Django 3.1.6 on 2022-02-04 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0053_auto_20211228_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='type_code',
            name='for_office',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]