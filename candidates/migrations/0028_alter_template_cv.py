# Generated by Django 5.1.2 on 2024-12-09 03:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0027_alter_template_cv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='cv',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cv_template', to='candidates.cv'),
        ),
    ]
