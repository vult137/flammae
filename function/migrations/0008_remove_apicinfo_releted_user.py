# Generated by Django 2.0.3 on 2018-05-16 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('function', '0007_auto_20180516_1730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apicinfo',
            name='releted_user',
        ),
    ]
