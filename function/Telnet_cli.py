from Exscript.protocols import SSH2, Telnet, exception
from Exscript import Host, Account
import types


class TelnetCLI:

    def __init__(self, ip=None, port=23, username=None, password=None,
                 timeout=3, link_right_now=False):
        self.target_ip = ip
        self.target_port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.connection = None
        self.port_num = None
        if link_right_now is True:
            if username is None or password is None or ip is None:
                raise Exception('Too few arguments')
            self.connect_to_target(self.username, self.password)

    @staticmethod
    def check_ip_legality(ip):
        if not isinstance(ip, str):
            return False
        addr = ip.strip().split('.')
        if len(addr) != 4:
            return False
        for i in range(4):
            if not addr[i].isdigit():
                return False
            if int(addr[i]) < 0 or int(addr[i]) > 255:
                return False
        return True

    @staticmethod
    def check_netmask_legality(netmask):
        if not TelnetCLI.check_ip_legality(netmask):
            return False
        addr = netmask.strip().split('.')
        marker = 0
        for i in range(4):
            if marker == 1 and addr[3 - i] != '255':
                return False
            tmp = 256 - int(addr[3 - i])
            if (tmp - 1) & tmp:
                return False
            if addr[3 - i] == '255':
                marker = 1
        return True

    def connect_to_target(self, username, password):
        self.username = username
        self.password = password
        timeout = self.timeout
        try:
            self.connection = Telnet(timeout=timeout)
            self.connection.connect(hostname=self.target_ip, port=self.target_port)
            self.connection.login(Account(self.username, self.password))
            self.get_device_port_info()
        except Exception:
            raise Exception('Fail to set up connection')

    @staticmethod
    def prefix_to_netmask(prefix):
        if type(prefix) is str:
            if prefix.isdigit():
                prefix = int(prefix)
            else:
                return None
        if prefix == 24:
            return '255.255.255.0'
        elif prefix == 30:
            return '255.255.255.252'

    def config_mode(self):
        self.connection.execute('conf t')

    def exit_config_mode(self):
        if self.check_config_mode() is True:
            self.connection.execute('exit')
        else:
            pass

    def check_config_mode(self):
        try:
            self.connection.execute('show int status')
            return False
        except exception.InvalidCommandException:
            return True

    def get_device_port_info(self):
        if self.check_config_mode():
            self.exit_config_mode()

        self.connection.execute('show ip int bri')
        response = self.connection.response
        GE_port_num = response.count('GigabitEthernet')
        FE_port_num = response.count('FastEthernet')

        self.port_num = GE_port_num + FE_port_num
        return {'FastEthernet port number': FE_port_num,
                'GigabitEthernet port number': GE_port_num,
                'Total port number': FE_port_num + GE_port_num,}

    def set_port_vlan(self, switchport, vlan):
        if switchport <= 1 or switchport > self.port_num:
            raise ValueError('No such port')

        if self.check_config_mode() is False:
            self.config_mode()
        self.connection.execute('int gi0/' + str(switchport))
        self.connection.execute('switchport access vlan ' + str(vlan))

    def get_port_vlan(self, switchport):
        if switchport < 1 or switchport > self.port_num:
            raise ValueError('No such port')

        if self.check_config_mode() is True:
            self.exit_config_mode()
        self.connection.execute('show run int gi0/' + str(switchport))

        result = self.connection.response
        pos = result.find('vlan')

        if pos == -1:
            return 1

        if result[pos + 6].isdigit():
            return result[pos + 5] + result[pos + 6]
        else:
            return result[pos + 5]

    def cancel_port_vlan(self, switch_port):
        self.set_port_vlan(switch_port, 1)

    def get_all_vlan(self):
        if self.check_config_mode() is True:
            self.exit_config_mode()
        self.connection.execute('show vlan bri')
        result = self.connection.response
        item_list = result.split('\r\n')[4:]
        # TODO: FINISH
        return item_list

    def get_vlan_info(self, vlan):
        try:
            if self.check_config_mode() is True:
                self.exit_config_mode()
            self.connection.execute('show vlan id ' + str(vlan))

            info = self.connection.response
            info = info[info.find('Ports') + 6:]
            info = info[info.find(str(vlan)) + len(str(vlan)):]

            ptr = 0

            # strip the space in text
            while info[ptr] == ' ':
                ptr += 1
            info = info[ptr:]
            ptr = 0

            # a method to get the word
            while info[ptr] != ' ' and info[ptr] != '\r' and info[ptr] != '\n':
                ptr += 1
            vlan_name = info[:ptr]
            info = info[ptr:]
            ptr = 0

            while info[ptr] == ' ':
                ptr += 1
            info = info[ptr:]
            ptr = 0

            while info[ptr] != ' ' and info[ptr] != '\r' and info[ptr] != '\n':
                ptr += 1
            vlan_status = info[:ptr]
            info = info[ptr:]
            ptr = 0

            # the port for port in the vlan
            port_list = []
            while info[ptr] == ' ':
                ptr += 1
            info = info[ptr:]
            ptr = 0

            position = info.find('Gi0/')
            while position != -1:
                if info[position + 5].isdigit():
                    port_list.append(int(info[position + 4: position + 6]))
                else:
                    port_list.append(int(info[position + 4]))
                info = info[position + 4:]
                position = info.find('Gi0/')

            r_json = {
                'id': vlan,
                'name': vlan_name,
                'status': vlan_status,
                'port_list': port_list,
            }

            return r_json
        except exception.InvalidCommandException:
            return {'error_msg': 'No vlan ' + str(vlan) + ' in switch.'}

    def create_vlan(self, **kwargs):
        if not self.check_config_mode():
            self.config_mode()
        vlan = kwargs.get('vlan')
        if vlan is not None:
            self.connection.execute('vlan ' + str(vlan))
        else:
            vlan_list = kwargs.get('vlan_list')
            if vlan_list:
                for v in vlan_list:
                    self.connection.execute('vlan ' + str(v))
            else:
                raise KeyError
        self.connection.execute('end')

    def delete_vlan(self, vlan):
        if vlan == 1:
            raise ValueError('Can\'t remove default vlan', vlan)

        if self.check_config_mode() is False:
            self.config_mode()

        try:
            port_list = self.get_vlan_info(vlan=vlan)['port_list']
            for port in port_list:
                self.cancel_port_vlan(switch_port=port)
            self.connection.execute('no vlan ' + str(vlan))
        except exception.InvalidCommandException:
            pass

    def get_cdp_info(self):
        if self.check_config_mode():
            self.exit_config_mode()
        self.connection.execute('show cdp neighbors')
        result = self.connection.response
        device_list = []
        position = result.find('Port ID') + 9
        result = result[position:]

        temp_list = ['Device ID', 'Local interface', 'Holdtime', 'Capability', 'Platform', 'Port ID', 'test']

        while True:
            position = 0
            position_e = result.find('\r\n')
            line = result[position:position_e]
            result = result[position_e + 1:]

            if len(line) <= 5:
                break

            temp = ''
            temp_device = {}
            i = 0
            j = 0

            while j < len(line):
                if line[j] == ' ' and line[j + 1] == ' ':
                    temp_device[temp_list[i]] = temp
                    while line[j] == ' ':
                        j += 1
                    temp = ''
                    i += 1
                else:
                    temp += line[j]
                    j += 1
            temp_device[temp_list[i]] = temp

            device_list.append(temp_device)
        return device_list

    def set_port_mode_trunk(self, switchport):
        if switchport <= 1 or switchport > self.port_num:
            raise ValueError('No such port')
        if not self.check_config_mode():
            self.config_mode()

        self.connection.execute('int gi0/' + str(switchport))
        self.connection.execute('switchport mode trunk')
        self.exit_config_mode()

    def check_port_mode_trunk(self, switchport):
        if switchport < 1 or switchport > self.port_num:
            raise ValueError('No such port')
        if self.check_config_mode():
            self.exit_config_mode()

        self.connection.execute('show run int gi0/' + str(switchport))
        result = self.connection.response
        if result.find('switchport mode trunk') == -1:
            return False
        return True

    def get_trunk_port(self):
        if self.check_config_mode():
            self.exit_config_mode()
        r_json = []
        for i in range(1, 13):
            r_json.append(self.check_port_mode_trunk(switchport=i))
        return r_json

    def set_port_trunk_accept_vlan(self, switchport, vlan_list):
        if switchport <= 1 or switchport > self.port_num:
            raise ValueError('No such port')

        if self.check_port_mode_trunk(switchport=switchport) is False:
            raise Exception('Not a trunk port')

        if not self.check_config_mode():
            self.config_mode()
        self.connection.execute('int gi0/' + str(switchport))
        v_list = ''
        for vlan in vlan_list:
            v_list += str(vlan) + ','
        v_list = v_list[0:-1]
        self.connection.execute('switchport trunk allowed vlan ' + v_list)
        self.exit_config_mode()

    def get_port_trunk_accept_vlan_list(self, switchport):
        if switchport <= 1 or switchport >self.port_num:
            raise ValueError('No such port')
        if not self.check_port_mode_trunk(switchport=switchport):
            raise Exception('Not trunk mode')

        ret_list = []
        if self.check_config_mode():
            self.exit_config_mode()

        self.connection.execute('show run int gi0/' + str(switchport))
        result = self.connection.response
        position = result.find('switchport trunk allowed vlan')
        result = result[position + 30:]
        position = result.find('\r\n')
        result = result[:position]
        tmp_lsit = result.split(',')
        for item in tmp_lsit:
            position = item.find('-')
            if position != -1:
                for i in range(int(item[position-1]), int(item[position+1])+1):
                    ret_list.append(i)
            else:
                ret_list.append(int(item))
        return ret_list

    def set_vlan_ip_address(self, vlan, ipaddr, netmask):
        if vlan == 1:
            raise ValueError('Cannot modify the default vlan')
        r_json = self.get_vlan_info(vlan=vlan)
        if 'error_msg' in r_json:
            raise ValueError(r_json['error_msg'])
        if not self.check_ip_legality(ipaddr):
            raise ValueError('Invalid ip address')
        if not self.check_netmask_legality(netmask):
            raise ValueError('Invalid netmask')
        if not self.check_config_mode():
            self.config_mode()

        self.connection.execute('int vlan ' + str(vlan))
        self.connection.execute('ip address ' + ipaddr + ' ' + netmask)
        self.exit_config_mode()

    def get_access_list(self):
        if self.check_config_mode() is True:
            self.exit_config_mode()
        self.connection.execute('show access-lists')
        result = self.connection.response
        # TODO: Use NetMiko library in this function !!!
        return result

    def get_system_temprature(self):
        if self.check_config_mode():
            self.exit_config_mode()
        self.connection.execute('show env all')
        response = self.connection.response
        position = response.find('System Temperature Value:')
        if position == -1:
            raise ValueError('Switch error')
        ret_str = ''
        response = response[position + 26:]

        i = 0
        while response[i].isdigit():
            ret_str += response[i]
            i += 1

        return int(ret_str)

    def get_all_info_for_view(self):
        temperature = self.get_system_temprature()
        port_num = self.port_num
        port_status = []
        port_trunk_list = self.get_trunk_port()
        for i in range(1, port_num+1):
            p_json = {'port_id': i,
                      'port_vlan': self.get_port_vlan(switchport=i),
                      'port_is_trunk': port_trunk_list[i - 1],
                      }
            if port_trunk_list[i - 1] is True:
                p_json['port_accept_vlan'] = self.get_port_trunk_accept_vlan_list(switchport=i)
            port_status.append(p_json)

        r_json = {
            'ip': self.target_ip,
            'temperature': temperature,
            'port_num': port_num,
            'port_status': port_status,
        }

        return r_json



if __name__ == '__main__':
    switch = TelnetCLI(ip='10.74.82.35',)
    switch.connect_to_target(username='cisco', password='c1sco@1234')

    res = switch.get_all_vlan()
    print(res)
