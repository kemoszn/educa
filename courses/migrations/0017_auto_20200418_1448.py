# Generated by Django 2.0.5 on 2020-04-18 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_auto_20200418_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.FileField(default='course_poster/ui-ux.png', upload_to='course_poster'),
        ),
    ]
