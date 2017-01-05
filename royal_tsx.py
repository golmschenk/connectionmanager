"""
Code for managing Royal TSX connections via scripts.
"""
import copy
import uuid
from xml.etree import ElementTree


class RoyalTsx:
    """
    Class for managing Royal TSX connections.
    """

    def __init__(self, document_path):
        self.document_path = document_path
        self.tree = ElementTree.parse(self.document_path)
        self.root = self.tree.getroot()
        self.folders = self.root.findall('RoyalFolder')
        connections_folder = None
        for folder in self.folders:
            if folder.find('Name').text == 'Connections':
                connections_folder = folder
                break
        self.connections_folder_id = connections_folder.find('ID').text
        self.connections = self.root.findall('RoyalSSHConnection')

    def sync(self, virtual_machines):
        """
        Sync the Royal TSX document to the provided virtual machines.

        :param virtual_machines: The list of virtual machines to sync to.
        :type virtual_machines: list[VirtualMachine]
        """
        self.delete_existing_connections()
        stencil = next(connection for connection in self.connections if connection.find('Name').text == 'Stencil')
        for virtual_machine in virtual_machines:
            if virtual_machine.state == 'running':
                new_connection = copy.deepcopy(stencil)
                new_connection.find('Name').text = virtual_machine.name
                new_connection.find('CustomField1').text = virtual_machine.ip
                new_connection.find('ID').text = str(uuid.uuid4())
                new_connection.find('ParentID').text = self.connections_folder_id
                self.root.append(new_connection)
        self.tree.write(self.document_path)

    def delete_existing_connections(self):
        """
        Delete the existing connections in the document's connection folder.
        """
        for connection in self.connections:
            if connection.find('ParentID').text == self.connections_folder_id:
                self.root.remove(connection)
