# Generated by Django 2.0.5 on 2020-04-18 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_auto_20200418_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(upload_to='course_poster'),
        ),
    ]