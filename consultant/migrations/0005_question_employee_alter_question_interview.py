# Generated by Django 4.1.7 on 2023-03-17 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('consultant', '0004_alter_jobinterview_number_of_questions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='consultant.employee'),
        ),
        migrations.AlterField(
            model_name='question',
            name='interview',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='consultant.jobinterview'),
        ),
    ]