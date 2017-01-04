"""
Code to represent a virtual machine.
"""
import json
from subprocess import run, PIPE


class VirtualMachine:
    """
    A class to represent virtual machines.
    """

    def __init__(self, id_, name, state=None, ip=None):
        self.id = id_
        self.name = name
        self.state = state
        self.ip = ip

    @classmethod
    def list_from_azure(cls):
        """
        Creates a list of VirtualMachines from the Azure account.

        :return: The list of VirtualMachines.
        :rtype: list[VirtualMachine]
        """
        vm_list_json = cls.attain_json_from_azure_vm_list()
        virtual_machine_json_dict_list = json.loads(vm_list_json)
        virtual_machines = []
        for virtual_machine_json_dict in virtual_machine_json_dict_list:
            virtual_machines.append(cls.from_azure_list_json_dict(virtual_machine_json_dict))
        return virtual_machines

    @classmethod
    def attain_json_from_azure_vm_list(cls):
        """
        Retrieves the string for the JSON from the Azure `az vm list` command. Checks that the user is logged in.

        :return: The JSON string.
        :rtype: str
        """
        vm_list_completed_process = run(['az', 'vm', 'list'], stdout=PIPE, stderr=PIPE, encoding='utf-8')
        if vm_list_completed_process.stderr:
            print('Error retrieving virtual machine list:')
            print(vm_list_completed_process.stderr)
            exit(1)
        if 'Credentials have expired due to inactivity.' in vm_list_completed_process.stdout:
            print('Not logged in. Run `az login`.')
            exit(1)
        vm_list_json = vm_list_completed_process.stdout
        return vm_list_json

    @classmethod
    def from_azure_list_json_dict(cls, virtual_machine_json_dict):
        """
        Creates a VirtualMachine from an Azure JSON entry.

        :param virtual_machine_json_dict: The dictionary from the Azure JSON.
        :type virtual_machine_json_dict: dict[]
        :return: The new virtual machine.
        :rtype: VirtualMachine
        """
        id_ = virtual_machine_json_dict['id']
        name = virtual_machine_json_dict['name']
        virtual_machine = cls(id_=id_, name=name)
        virtual_machine.obtain_azure_state()
        if virtual_machine.state == 'running':
            virtual_machine.obtain_azure_ip()
        return virtual_machine

    def obtain_azure_state(self):
        """
        Retrieves the power state of the virtual machine and sets the attribute.
        """
        completed_process = run(['az', 'vm', 'get-instance-view', '--ids', self.id], stdout=PIPE, stderr=PIPE,
                                encoding='utf-8')
        json_string = completed_process.stdout
        json_dict = json.loads(json_string)
        statuses = json_dict['instanceView']['statuses']
        self.state = next(
            status['code'][len('PowerState/'):] for status in statuses if status['code'].startswith('PowerState/')
        )

    def obtain_azure_ip(self):
        """
        Retrieves the ip of the virtual machine and sets the attribute.
        """
        completed_process = run(['az', 'vm', 'list-ip-addresses', '--ids', self.id], stdout=PIPE, stderr=PIPE,
                                encoding='utf-8')
        json_string = completed_process.stdout
        json_dict = json.loads(json_string)
        self.ip = json_dict[0]['virtualMachine']['network']['publicIpAddresses'][0]['ipAddress']
