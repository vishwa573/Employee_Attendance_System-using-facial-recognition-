# Generated by Django 5.0.6 on 2024-06-27 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0020_location_name_alter_employee_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(default='Default Name', max_length=30),
        ),
    ]
