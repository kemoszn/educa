# Generated by Django 2.0.5 on 2020-04-18 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_auto_20200417_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='image',
            field=models.ImageField(upload_to='course_poster'),
            preserve_default=False,
        ),
    ]