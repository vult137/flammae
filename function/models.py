from django.db import models
from users.models import User

# Create your models here.


class Switch(models.Model):
    SWITCH_CHOICES = (
        (1, 'CiscoIOS'),
        (2, 'CiscoNx'),
        (3, 'Huawei'),
        (4, 'H3C'),
        (5, 'Juniper Junos'),
    )

    PORT_TYPE_CHOICES = (
        (1, 'GIGABITETHERNET'),
        (2, 'FASTETHERNET')
    )

    switch_ip = models.GenericIPAddressField()
    switch_username = models.CharField(max_length=50)
    switch_password = models.CharField(max_length=128)
    switch_type = models.IntegerField(choices=SWITCH_CHOICES)

    # NOTICE: the code added below could be wrong.
    switch_port_num = models.IntegerField(null=True, default=-1)
    switch_port_type = models.IntegerField(null=True, choices=PORT_TYPE_CHOICES, default=1)


class ApicInfo(models.Model):
    # TODO: finish this
    controller = models.URLField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    user_info = models.ForeignKey(User, on_delete=models.CASCADE)