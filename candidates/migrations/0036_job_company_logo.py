# Generated by Django 5.1.2 on 2024-12-30 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0035_alter_job_industry_alter_job_original_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='company_logo',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]
