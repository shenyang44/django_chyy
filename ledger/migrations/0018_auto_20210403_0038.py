# Generated by Django 3.1.6 on 2021-04-02 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0017_auto_20210402_0058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client_account',
            name='account_no',
        ),
        migrations.AddField(
            model_name='client_account',
            name='name',
            field=models.TextField(default='fail', unique=True),
            preserve_default=False,
        ),
    ]
