# Generated by Django 2.0.5 on 2020-04-13 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_auto_20200413_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='instructor',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
