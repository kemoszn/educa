# Generated by Django 2.0.5 on 2020-04-18 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0015_auto_20200418_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='course_poster'),
        ),
    ]
