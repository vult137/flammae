# Generated by Django 2.0.3 on 2018-04-30 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='auth',
            field=models.IntegerField(choices=[(1, 'ViewAuth'), (2, 'EnableAuth')], default=1),
        ),
    ]
