# Generated by Django 2.0.3 on 2018-05-16 09:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('function', '0005_auto_20180516_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apicinfo',
            name='releted_user',
            field=models.ForeignKey(default='HAHA', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
