# Generated by Django 2.0.3 on 2018-05-09 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('function', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='switch_port_num',
            field=models.IntegerField(default=-1, null=True),
        ),
        migrations.AddField(
            model_name='switch',
            name='switch_port_type',
            field=models.IntegerField(choices=[(1, 'GIGABITETHERNET'), (2, 'FASTETHERNET')], default=1, null=True),
        ),
    ]
