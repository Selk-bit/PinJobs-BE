# Generated by Django 5.1.2 on 2024-11-25 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0015_job_job_id_alter_job_original_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='cvdata',
            name='yoe',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
