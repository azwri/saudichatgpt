# Generated by Django 4.1.7 on 2023-03-17 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobinterview',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
