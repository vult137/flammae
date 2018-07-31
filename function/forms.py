from function.models import Switch
from function.Telnet_cli import TelnetCLI
from django.core.exceptions import ValidationError
from django import forms


class SwitchForm(forms.ModelForm):

    class Meta:
        model = Switch
        fields = ('switch_ip', 'switch_username', 'switch_password', 'switch_type')

    def clean(self):
        ip = self.cleaned_data.get('switch_ip')
        username = self.cleaned_data.get('switch_username')
        password = self.cleaned_data.get('switch_password')
        try:
            swithc_handler = TelnetCLI(ip=ip, username=username, password=password, link_right_now=True)
            swithc_handler.check_config_mode()
        except Exception:
            raise ValidationError('Wrong information.')

        return self.cleaned_data
