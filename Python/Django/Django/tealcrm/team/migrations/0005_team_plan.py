# Generated by Django 4.2.4 on 2024-01-11 09:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0004_remove_team_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='plan',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='team.plan'),
            preserve_default=False,
        ),
    ]