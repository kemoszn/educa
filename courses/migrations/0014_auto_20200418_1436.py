# Generated by Django 2.0.5 on 2020-04-18 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_auto_20200418_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(blank=True, upload_to='course_poster'),
        ),
    ]
