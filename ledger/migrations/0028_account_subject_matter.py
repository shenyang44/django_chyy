# Generated by Django 3.1.6 on 2021-04-15 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0027_account_client_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='subject_matter',
            field=models.TextField(default='example matter'),
            preserve_default=False,
        ),
    ]