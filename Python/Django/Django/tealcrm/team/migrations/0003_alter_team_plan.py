# Generated by Django 4.2.4 on 2024-01-11 08:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_plan_team_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='team.plan'),
        ),
    ]
