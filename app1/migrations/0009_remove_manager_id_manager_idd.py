# Generated by Django 5.0.6 on 2024-06-11 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0008_manager_remove_employee_is_manager'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manager',
            name='id',
        ),
        migrations.AddField(
            model_name='manager',
            name='idd',
            field=models.IntegerField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
