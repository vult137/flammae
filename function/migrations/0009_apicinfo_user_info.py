# Generated by Django 2.0.3 on 2018-05-17 06:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('function', '0008_remove_apicinfo_releted_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='apicinfo',
            name='user_info',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]