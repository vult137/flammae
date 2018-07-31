from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from requests.exceptions import ConnectionError
from django.core.exceptions import ObjectDoesNotExist

from os import path
import json

from function.Telnet_cli import TelnetCLI
from function.APIC_rest import APICrestful
from function.forms import SwitchForm
from function.models import Switch, ApicInfo


@login_required
def add_switch(request):
    redirect_to = request.POST.get('next', request.GET.get('next', ''))
    error_list = []
    if request.method == 'POST':
        form = SwitchForm(request.POST)
        if form.is_valid():
            form.save()
            if redirect_to:
                return redirect(redirect_to)
            else:
                return redirect('/')
        else:
            pass
    else:
        form = SwitchForm()
    return render(request, 'function/switch_add.html', context={'form': form,
                                                                'redirect_to': redirect_to, 'errors': error_list})


@login_required
def switch_view_all(request, query_file=False):
    switches = Switch.objects.all()
    switch_info_list = []

    if query_file is True:
        for switch in switches:
            try:
                pk = switch.pk
                file_name = 'switch_temp_info_pk_{pk}.json'.format(pk=pk)
                file_dir = './function/temp/' + file_name
                temp_json_file = open(file_dir, 'r')
                read_content = temp_json_file.read()
                temp_json = json.loads(read_content)
                switch_info_list.append(temp_json)
            except FileNotFoundError:
                switch_handler = TelnetCLI(ip=switch.switch_ip, username=switch.switch_username,
                                           password=switch.switch_password, link_right_now=True)
                temperature = switch_handler.get_system_temprature()
                port_num = switch_handler.port_num
                port_status = []
                port_trunk_list = switch_handler.get_trunk_port()
                for i in range(1, port_num + 1):
                    p_json = {'port_id': i,
                              'port_vlan': switch_handler.get_port_vlan(switchport=i),
                              'port_is_trunk': port_trunk_list[i - 1],
                              }
                    if port_trunk_list[i - 1] is True:
                        p_json['port_accept_vlan'] = switch_handler.get_port_trunk_accept_vlan_list(switchport=i)
                    port_status.append(p_json)

                pk = switch.id
                switch_info = {
                    'pk': pk,
                    'ip': switch.switch_ip,
                    'temperature': temperature,
                    'port_num': port_num,
                    'port_status': port_status,
                }
                switch_info_list.append(switch_info)
    else:
        for switch in switches:
            switch_handler = TelnetCLI(ip=switch.switch_ip, username=switch.switch_username,
                                       password=switch.switch_password, link_right_now=True)
            temperature = switch_handler.get_system_temprature()
            port_num = switch_handler.port_num
            port_status = []
            port_trunk_list = switch_handler.get_trunk_port()
            for i in range(1, port_num+1):
                p_json = {'port_id': i,
                          'port_vlan': switch_handler.get_port_vlan(switchport=i),
                          'port_is_trunk': port_trunk_list[i - 1],
                          }
                if port_trunk_list[i - 1] is True:
                    p_json['port_accept_vlan'] = switch_handler.get_port_trunk_accept_vlan_list(switchport=i)
                port_status.append(p_json)

            pk = switch.id
            switch_info = {
                'pk': pk,
                'ip': switch.switch_ip,
                'temperature': temperature,
                'port_num': port_num,
                'port_status': port_status,
            }
            switch_info_list.append(switch_info)
            file_name = 'switch_temp_info_pk_{pk}.json'.format(pk=pk)
            file_dir = './function/temp/' + file_name
            temp_json_file = open(file_dir, 'w')
            temp_json_file.write(json.dumps(switch_info))
            temp_json_file.close()

    return render(request, 'function/switch_all.html', context={'switch_list': switch_info_list})


@login_required
def switch_modify(request, pk):
    switch = get_object_or_404(Switch, pk=pk)

    if request.method == 'GET':
        read_file_in = False
        context_payload = {}
        try:
            file_name = 'switch_temp_info_pk_{pk}.json'.format(pk=pk)
            file_dir = './function/temp/' + file_name
            temp_json_file = open(file_dir, 'r')
            read_content = temp_json_file.read()
            temp_json = json.loads(read_content)
            for key in temp_json:
                context_payload[key] = temp_json[key]
            read_file_in = True
        except FileNotFoundError:
            switch_handler = TelnetCLI(ip=switch.switch_ip, username=switch.switch_username,
                                       password=switch.switch_password, link_right_now=True)
            temperature = switch_handler.get_system_temprature()
            port_num = switch_handler.port_num
            port_status = []
            port_trunk_list = switch_handler.get_trunk_port()
            for i in range(1, port_num + 1):
                p_json = {'port_id': i,
                          'port_vlan': switch_handler.get_port_vlan(switchport=i),
                          'port_is_trunk': port_trunk_list[i - 1],
                          }
                if port_trunk_list[i - 1] is True:
                    p_json['port_accept_vlan'] = switch_handler.get_port_trunk_accept_vlan_list(switchport=i)
                port_status.append(p_json)
            pk = switch.id
            context_payload = {
                'pk': pk,
                'ip': switch.switch_ip,
                'temperature': temperature,
                'port_num': port_num,
                'port_status': port_status,
            }
        return render(request, 'function/switch_modify.html', context=context_payload)

    if request.method == 'POST':
        switch_handler = TelnetCLI(ip=switch.switch_ip, username=switch.switch_username,
                                   password=switch.switch_password, link_right_now=True)
        select_port = request.POST.get('port_select')
        vlan = request.POST.get('set_vlan')

        select_port = int(select_port)
        vlan = int(vlan)

        if 'error_msg' in switch_handler.get_vlan_info(vlan=vlan):
            switch_handler.create_vlan(vlan=vlan)

        switch_handler.set_port_vlan(switchport=select_port, vlan=vlan)
        return switch_view_all(request, query_file=True)


@login_required
def apic_login(request):
    if request.method == 'POST':
        controller = request.POST.get('controller')
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            apic_rest = APICrestful(controller=controller, auth={"username": username, "password": password})
            apic_rest.ticket = apic_rest.get_ticket()
            if len(ApicInfo.objects.filter(user_info=request.user, controller=controller)) != 0:
                return HttpResponse('<p>改控制器已在列表中</p>')
        except KeyError:
            return HttpResponse('<p>账号密码有误，无法添加</p>')
        except ConnectionError or json.JSONDecodeError:
            return HttpResponse('<p>控制器有误</p>')

        apic_info = ApicInfo(controller=controller, username=username,
                             password=password, user_info=request.user)
        apic_info.save()
        return HttpResponse('<p>添加账户成功成功</p>')
    else:
        return render(request, 'function/apic_login.html',)


@login_required
def apic_query(request):
    apic_info_list = ApicInfo.objects.filter(user_info=request.user)
    return render(request, 'function/apic_query.html', context={'apic_info_list': apic_info_list})


def apic_query_detail(request, pk):
    try:
        apic_info = ApicInfo.objects.get(user_info=request.user, pk=pk)
        apic_handler = APICrestful(controller=apic_info.controller, auth={
            'username': apic_info.username,
            'password': apic_info.password,
        })
        data = {
            'apic_info': apic_info,
            'device_list': apic_handler.get_devices(),
        }
        return render(request, 'function/apic_query_detail.html', context={'data': data})
    except ObjectDoesNotExist:
        return HttpResponse('<p>没有相关信息</p>')


def apic_query_vlan(request, pk):
    try:
        apic_info = ApicInfo.objects.get(user_info=request.user, pk=pk)
        apic_handler = APICrestful(controller=apic_info.controller, auth={
            'username': apic_info.username,
            'password': apic_info.password,
        })
        apic_vlan_list = apic_handler.get_apic_vlan_list()
        file_save(apic_vlan_list, pk)
        switches = Switch.objects.all()
        return render(request, 'function/apic_query_detail.html',
                      context={'vlan_list': apic_vlan_list, 'switch_list': switches})
    except ObjectDoesNotExist:
        return HttpResponse('<p>没有相关信息</p>')


def deliver_apic_vlan_config(request, pk):
    if request.method == 'POST':
        select_switch = request.POST.get('switch_select')
        switch = Switch.objects.get(id=select_switch)
        switch_handler = TelnetCLI(ip=switch.switch_ip, username=switch.switch_username,
                                   password=switch.switch_password, link_right_now=True)
        vlan_info_list = read_file(pk=pk)
        for vlan_group in vlan_info_list:
            for vlan_info in vlan_group:
                try:
                    if vlan_info['interfaceName'] == 'Vlan1' or vlan_info['vlanNumber'] == 1:
                        continue
                    vlan_number = vlan_info['vlanNumber']
                    ip_address = vlan_info['ipAddress']
                    prefix = vlan_info['prefix']
                    switch_handler.create_vlan(vlan=vlan_info['vlanNumber'])
                    switch_handler.set_vlan_ip_address(vlan=vlan_number, ipaddr=ip_address,
                                                       netmask=TelnetCLI.prefix_to_netmask(prefix=prefix))
                except KeyError:
                    pass
        return HttpResponse('<h1>成功配置</h1>')
    else:
        return HttpResponse('No no no.')


def file_save(i_json, pk):
    file_name = './function/temp/apic_vlan_temp_info_{id}.json'.format(id=pk)
    file = open(file_name, 'w')
    file.write(json.dumps(i_json))
    file.close()


def read_file(pk):
    file_name = './function/temp/apic_vlan_temp_info_{id}.json'.format(id=pk)
    file = open(file_name, 'r')
    r_json = json.loads(file.read())
    file.close()
    return r_json
