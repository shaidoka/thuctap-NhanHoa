# Generated by Django 4.2.4 on 2024-01-11 08:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0002_client_team'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ('name',)},
        ),
    ]