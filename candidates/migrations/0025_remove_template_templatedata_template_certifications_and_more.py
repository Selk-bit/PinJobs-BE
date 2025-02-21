# Generated by Django 5.1.2 on 2024-12-08 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0024_remove_abstracttemplate_language_template_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='template',
            name='templateData',
        ),
        migrations.AddField(
            model_name='template',
            name='certifications',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='company_logo',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='education',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='experience',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='interests',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='languages',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='page',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='personnel',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='projects',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='references',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='skills',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='social',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='theme',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='typography',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='template',
            name='volunteering',
            field=models.JSONField(default=dict),
        ),
        migrations.DeleteModel(
            name='Modele',
        ),
    ]
